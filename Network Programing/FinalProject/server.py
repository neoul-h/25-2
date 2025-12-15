from socket import *
import threading
import secrets
import time
import os
import base64

HOST = "0.0.0.0"
PORT = 6000

BOOK_FILE = "agent_book.txt"

# agentId -> {"pass": str, "level": int}
AGENT_BOOK = {}
book_lock = threading.Lock()

agents = {}          # agentId -> socket
agents_lock = threading.Lock()

# SID -> {"agent": id, "level": int, "shift": int}
sessions = {}
sessions_lock = threading.Lock()

sock_buffers = {}    # sock -> partial buffer
buf_lock = threading.Lock()

# sock -> (agent_id, nonce, level)
challenges = {}
chal_lock = threading.Lock()

# msg_id -> {"from":, "to":, "payload_b64":}
once_store = {}
once_lock = threading.Lock()

# msg_id -> {"sender": id, "sender_sock": sock, "pending": set(ids), "kind": str}
ack_track = {}
ack_lock = threading.Lock()

# LEVEL4 only: lockdown
lockdown = False
lock_lock = threading.Lock()

# logs
LOG_MAX = 200
log_buf = []
log_lock = threading.Lock()


def b64_enc(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def b64_dec(s: str) -> str:
    return base64.b64decode(s.encode()).decode()


def log_event(text):
    ts = time.strftime("%H:%M:%S")
    line = f"{ts} {text}"
    with log_lock:
        log_buf.append(line)
        if len(log_buf) > LOG_MAX:
            del log_buf[0]


def send_line(sock, line):
    if not line.endswith("\n"):
        line += "\n"
    try:
        sock.sendall(line.encode())
    except:
        pass


def parse_lines(sock, data_bytes):
    text = data_bytes.decode(errors="ignore")
    with buf_lock:
        prev = sock_buffers.get(sock, "")
        prev += text
        lines = prev.split("\n")
        sock_buffers[sock] = lines[-1]
    return [ln.strip() for ln in lines[:-1] if ln.strip()]


def make_proof(agent_id, nonce):
    # 인증 검증 규칙(암호화 아님)
    return str(nonce)[::-1] + "-" + str(len(agent_id))


def create_session(agent_id, nonce, level):
    sid = "SID-" + secrets.token_hex(8)
    shift = nonce % 26
    with sessions_lock:
        sessions[sid] = {"agent": agent_id, "level": level, "shift": shift}
    return sid, shift


def get_session(sid):
    with sessions_lock:
        return sessions.get(sid)


def auth_required(sock, sid):
    sess = get_session(sid)
    if not sess:
        send_line(sock, "FAIL:AUTH:BAD_SID:")
        return None
    return sess


def is_locked_down_for(sess):
    with lock_lock:
        if not lockdown:
            return False
    return sess["level"] < 4


def require_level(sock, sess, need_level, action):
    if sess["level"] < need_level:
        send_line(sock, f"FAIL:{action}:NO_PERMISSION:")
        return False
    return True


def ack_register(msg_id, sender_id, sender_sock, recipients, kind):
    with ack_lock:
        ack_track[msg_id] = {
            "sender": sender_id,
            "sender_sock": sender_sock,
            "pending": set(recipients),
            "kind": kind,
        }


def ack_mark(agent_id, msg_id):
    with ack_lock:
        item = ack_track.get(msg_id)
        if not item:
            return None
        pending = item["pending"]
        if agent_id in pending:
            pending.remove(agent_id)
        done = (len(pending) == 0)
        sender_sock = item["sender_sock"]
        kind = item["kind"]
        if done:
            del ack_track[msg_id]
        return done, sender_sock, kind


def remove_agent_by_sock(sock):
    dead = []
    with agents_lock:
        for aid, s in list(agents.items()):
            if s == sock:
                dead.append(aid)
                del agents[aid]
    if dead:
        with sessions_lock:
            for sid, info in list(sessions.items()):
                if info.get("agent") in dead:
                    del sessions[sid]
    return dead


# ───────────────────────────── 코드북 파일 I/O ─────────────────────────────

def ensure_default_book_file():
    if os.path.exists(BOOK_FILE):
        return
    sample = [
        "# agentId passcode level",
        "aaa APPLE 1",
        "bbb BANANA 2",
        "neo ZION 3",
        "boss ROOT 4",
        "",
    ]
    with open(BOOK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sample))


def load_book():
    """BOOK_FILE -> AGENT_BOOK"""
    with book_lock:
        AGENT_BOOK.clear()
        with open(BOOK_FILE, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 3:
                    continue
                aid, pw, lv = parts[0], parts[1], parts[2]
                try:
                    lv = int(lv)
                except:
                    continue
                if lv < 1 or lv > 4:
                    continue
                AGENT_BOOK[aid] = {"pass": pw, "level": lv}


def save_book():
    """AGENT_BOOK -> BOOK_FILE"""
    with book_lock:
        lines = ["# agentId passcode level"]
        for aid in sorted(AGENT_BOOK.keys()):
            pw = AGENT_BOOK[aid]["pass"]
            lv = AGENT_BOOK[aid]["level"]
            lines.append(f"{aid} {pw} {lv}")
        lines.append("")
        with open(BOOK_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def book_get(aid):
    with book_lock:
        return AGENT_BOOK.get(aid)


def book_set(aid, pw, lv):
    with book_lock:
        AGENT_BOOK[aid] = {"pass": pw, "level": lv}


def book_del(aid):
    with book_lock:
        if aid in AGENT_BOOK:
            del AGENT_BOOK[aid]


# ───────────────────────────── Handlers ─────────────────────────────

def handle_hello(sock, parts):
    # HELLO:agentId:passcode:
    if len(parts) < 3 or not parts[1] or not parts[2]:
        send_line(sock, "AUTH_FAIL:FORMAT:")
        return

    agent_id = parts[1]
    passcode = parts[2].strip()

    info = book_get(agent_id)
    if not info:
        send_line(sock, "AUTH_FAIL:UNKNOWN_AGENT:")
        return
    if passcode != info["pass"]:
        send_line(sock, "AUTH_FAIL:BAD_PASSCODE:")
        return

    with agents_lock:
        if agent_id in agents:
            send_line(sock, "AUTH_FAIL:DUP_ID:")
            return

    level = int(info["level"])
    nonce = secrets.randbelow(9000) + 1000

    with chal_lock:
        challenges[sock] = (agent_id, nonce, level)

    send_line(sock, f"CHALLENGE:{nonce}:")
    log_event(f"[HELLO] agent={agent_id} level={level} challenge={nonce}")


def handle_response(sock, parts):
    # RESPONSE:agentId:proof:
    if len(parts) < 3:
        send_line(sock, "AUTH_FAIL:FORMAT:")
        return

    agent_id, proof = parts[1], parts[2]

    with chal_lock:
        item = challenges.get(sock)
    if not item:
        send_line(sock, "AUTH_FAIL:NO_CHALLENGE:")
        return

    expect_agent, nonce, level = item
    if agent_id != expect_agent:
        send_line(sock, "AUTH_FAIL:ID_MISMATCH:")
        return
    if proof != make_proof(agent_id, nonce):
        send_line(sock, "AUTH_FAIL:BAD_PROOF:")
        return

    sid, shift = create_session(agent_id, nonce, level)

    with agents_lock:
        agents[agent_id] = sock
    with chal_lock:
        del challenges[sock]

    send_line(sock, f"AUTH_OK:{sid}:{level}:{shift}:")
    print(f"[AUTH_OK] agent={agent_id}, sid={sid}, level={level}, shift={shift}")
    log_event(f"[AUTH_OK] agent={agent_id} sid={sid} level={level} shift={shift}")


def handle_ping(sock, parts):
    # PING:SID:
    if len(parts) < 2:
        return
    sid = parts[1]
    if not get_session(sid):
        return
    send_line(sock, "PONG:")


def handle_list(sock, parts):
    # LIST:SID:
    if len(parts) < 2:
        send_line(sock, "FAIL:LIST:FORMAT:")
        return
    sess = auth_required(sock, parts[1])
    if not sess:
        return

    with agents_lock:
        ids = list(agents.keys())
    send_line(sock, "AGENTS:" + ",".join(ids) + ":")


def handle_dm(sock, parts):
    # DM:SID:TO:MSG_ID:payload_b64:
    if len(parts) < 5:
        send_line(sock, "FAIL:DM:FORMAT:")
        return
    sid, to_id, msg_id, payload_b64 = parts[1], parts[2], parts[3], parts[4]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if is_locked_down_for(sess):
        send_line(sock, "FAIL:DM:LOCKDOWN:")
        return

    from_id = sess["agent"]
    if from_id == to_id:
        send_line(sock, "FAIL:DM:NO_SELF:")
        return

    with agents_lock:
        target = agents.get(to_id)
    if not target:
        send_line(sock, "FAIL:DM:NO_TARGET:")
        return

    send_line(target, f"DELIVER_DM:{from_id}:{msg_id}:{payload_b64}:")
    ack_register(msg_id, from_id, sock, [to_id], "DM")
    send_line(sock, "OK:DM:")
    log_event(f"[DM] {from_id} -> {to_id} ({msg_id})")


def handle_bcast(sock, parts):
    # BCAST:SID:MSG_ID:payload_b64:
    if len(parts) < 4:
        send_line(sock, "FAIL:BCAST:FORMAT:")
        return
    sid, msg_id, payload_b64 = parts[1], parts[2], parts[3]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if is_locked_down_for(sess):
        send_line(sock, "FAIL:BCAST:LOCKDOWN:")
        return

    if not require_level(sock, sess, 3, "BCAST"):
        return

    from_id = sess["agent"]
    recipients = []
    with agents_lock:
        for aid, cs in agents.items():
            if aid == from_id:
                continue
            recipients.append(aid)
            send_line(cs, f"DELIVER_BCAST:{from_id}:{msg_id}:{payload_b64}:")

    ack_register(msg_id, from_id, sock, recipients, "BCAST")
    send_line(sock, "OK:BCAST:")
    log_event(f"[BCAST] {from_id} -> ALL ({msg_id})")


def handle_ack(sock, parts):
    # ACK:SID:MSG_ID:
    if len(parts) < 3:
        send_line(sock, "FAIL:ACK:FORMAT:")
        return
    sid, msg_id = parts[1], parts[2]
    sess = auth_required(sock, sid)
    if not sess:
        return

    agent_id = sess["agent"]
    res = ack_mark(agent_id, msg_id)
    send_line(sock, "OK:ACK:")

    if res:
        done, sender_sock, kind = res
        if done and sender_sock:
            send_line(sender_sock, f"ACK_DONE:{msg_id}:{kind}:")
            log_event(f"[ACK_DONE] msg={msg_id} kind={kind}")


def handle_once(sock, parts):
    # ONCE:SID:TO:MSG_ID:payload_b64:
    if len(parts) < 5:
        send_line(sock, "FAIL:ONCE:FORMAT:")
        return
    sid, to_id, msg_id, payload_b64 = parts[1], parts[2], parts[3], parts[4]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if is_locked_down_for(sess):
        send_line(sock, "FAIL:ONCE:LOCKDOWN:")
        return

    if not require_level(sock, sess, 2, "ONCE"):
        return

    from_id = sess["agent"]
    if from_id == to_id:
        send_line(sock, "FAIL:ONCE:NO_SELF:")
        return

    with agents_lock:
        target = agents.get(to_id)
    if not target:
        send_line(sock, "FAIL:ONCE:NO_TARGET:")
        return

    with once_lock:
        once_store[msg_id] = {"from": from_id, "to": to_id, "payload_b64": payload_b64}

    send_line(target, f"ONCE_NOTICE:{from_id}:{msg_id}:")
    send_line(sock, "OK:ONCE:")
    log_event(f"[ONCE] {from_id} -> {to_id} ({msg_id})")


def handle_read(sock, parts):
    # READ:SID:MSG_ID:
    if len(parts) < 3:
        send_line(sock, "FAIL:READ:FORMAT:")
        return
    sid, msg_id = parts[1], parts[2]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if is_locked_down_for(sess):
        send_line(sock, "FAIL:READ:LOCKDOWN:")
        return

    if not require_level(sock, sess, 2, "READ"):
        return

    reader = sess["agent"]
    with once_lock:
        item = once_store.get(msg_id)
        if not item:
            send_line(sock, "FAIL:READ:NO_SUCH_MSG:")
            return
        if item["to"] != reader:
            send_line(sock, "FAIL:READ:NOT_YOURS:")
            return
        payload_b64 = item["payload_b64"]
        sender = item["from"]
        del once_store[msg_id]

    send_line(sock, f"DELIVER_ONCE:{sender}:{msg_id}:{payload_b64}:")
    send_line(sock, f"DESTROYED:{msg_id}:")
    log_event(f"[READ+DESTROY] to={reader} msg={msg_id}")


# ───────────────────────────── LEVEL4: 코드북 관리 ─────────────────────────────

def handle_book_show(sock, parts):
    if len(parts) < 2:
        send_line(sock, "FAIL:BOOK_SHOW:FORMAT:")
        return
    sess = auth_required(sock, parts[1])
    if not sess:
        return
    if not require_level(sock, sess, 4, "BOOK_SHOW"):
        return

    with book_lock:
        items = [(aid, AGENT_BOOK[aid]["pass"], AGENT_BOOK[aid]["level"]) for aid in sorted(AGENT_BOOK.keys())]

    send_line(sock, "BOOKBEGIN:")
    for aid, pw, lv in items:
        send_line(sock, f"BOOKENTRY:{aid}:{pw}:{lv}:")
    send_line(sock, "BOOKEND:")
    send_line(sock, "OK:BOOK_SHOW:")
    log_event(f"[BOOK_SHOW] by={sess['agent']}")


def handle_book_add(sock, parts):
    if len(parts) < 5:
        send_line(sock, "FAIL:BOOK_ADD:FORMAT:")
        return
    sid, aid, pw, lv_s = parts[1], parts[2], parts[3], parts[4]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "BOOK_ADD"):
        return

    try:
        lv = int(lv_s)
    except:
        send_line(sock, "FAIL:BOOK_ADD:BAD_LEVEL:")
        return
    if lv < 1 or lv > 4:
        send_line(sock, "FAIL:BOOK_ADD:BAD_LEVEL:")
        return
    if ":" in aid or ":" in pw or " " in aid or " " in pw:
        send_line(sock, "FAIL:BOOK_ADD:BAD_TOKEN:")
        return

    if book_get(aid) is not None:
        send_line(sock, "FAIL:BOOK_ADD:EXISTS:")
        return

    book_set(aid, pw, lv)
    save_book()
    send_line(sock, "OK:BOOK_ADD:")
    log_event(f"[BOOK_ADD] by={sess['agent']} add={aid} lv={lv}")


def handle_book_set(sock, parts):
    if len(parts) < 5:
        send_line(sock, "FAIL:BOOK_SET:FORMAT:")
        return
    sid, aid, pw, lv_s = parts[1], parts[2], parts[3], parts[4]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "BOOK_SET"):
        return

    try:
        lv = int(lv_s)
    except:
        send_line(sock, "FAIL:BOOK_SET:BAD_LEVEL:")
        return
    if lv < 1 or lv > 4:
        send_line(sock, "FAIL:BOOK_SET:BAD_LEVEL:")
        return

    if book_get(aid) is None:
        send_line(sock, "FAIL:BOOK_SET:NO_SUCH_AGENT:")
        return

    book_set(aid, pw, lv)
    save_book()
    send_line(sock, "OK:BOOK_SET:")
    log_event(f"[BOOK_SET] by={sess['agent']} set={aid} lv={lv}")


def handle_book_del(sock, parts):
    if len(parts) < 3:
        send_line(sock, "FAIL:BOOK_DEL:FORMAT:")
        return
    sid, aid = parts[1], parts[2]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "BOOK_DEL"):
        return

    if book_get(aid) is None:
        send_line(sock, "FAIL:BOOK_DEL:NO_SUCH_AGENT:")
        return

    book_del(aid)
    save_book()
    send_line(sock, "OK:BOOK_DEL:")
    log_event(f"[BOOK_DEL] by={sess['agent']} del={aid}")


def handle_book_pass(sock, parts):
    if len(parts) < 4:
        send_line(sock, "FAIL:BOOK_PASS:FORMAT:")
        return
    sid, aid, newpass = parts[1], parts[2], parts[3]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "BOOK_PASS"):
        return

    info = book_get(aid)
    if info is None:
        send_line(sock, "FAIL:BOOK_PASS:NO_SUCH_AGENT:")
        return

    book_set(aid, newpass, int(info["level"]))
    save_book()
    send_line(sock, "OK:BOOK_PASS:")
    log_event(f"[BOOK_PASS] by={sess['agent']} agent={aid}")


def handle_book_level(sock, parts):
    if len(parts) < 4:
        send_line(sock, "FAIL:BOOK_LEVEL:FORMAT:")
        return
    sid, aid, lv_s = parts[1], parts[2], parts[3]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "BOOK_LEVEL"):
        return

    try:
        lv = int(lv_s)
    except:
        send_line(sock, "FAIL:BOOK_LEVEL:BAD_LEVEL:")
        return
    if lv < 1 or lv > 4:
        send_line(sock, "FAIL:BOOK_LEVEL:BAD_LEVEL:")
        return

    info = book_get(aid)
    if info is None:
        send_line(sock, "FAIL:BOOK_LEVEL:NO_SUCH_AGENT:")
        return

    book_set(aid, info["pass"], lv)
    save_book()
    send_line(sock, "OK:BOOK_LEVEL:")
    log_event(f"[BOOK_LEVEL] by={sess['agent']} agent={aid} lv={lv}")


# ───────────────────────────── 기타 LEVEL4 ─────────────────────────────

def handle_lock(sock, parts):
    # LOCK:SID:ON|OFF:
    if len(parts) < 3:
        send_line(sock, "FAIL:LOCK:FORMAT:")
        return
    sid, mode = parts[1], parts[2].upper()
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "LOCK"):
        return

    global lockdown
    if mode not in ("ON", "OFF"):
        send_line(sock, "FAIL:LOCK:BAD_MODE:")
        return

    with lock_lock:
        lockdown = (mode == "ON")

    send_line(sock, "OK:LOCK:")
    log_event(f"[LOCKDOWN] by={sess['agent']} mode={mode}")


def handle_log(sock, parts):
    # LOG:SID:N:
    if len(parts) < 3:
        send_line(sock, "FAIL:LOG:FORMAT:")
        return
    sid = parts[1]
    sess = auth_required(sock, sid)
    if not sess:
        return
    if not require_level(sock, sess, 4, "LOG"):
        return

    try:
        n = int(parts[2])
    except:
        send_line(sock, "FAIL:LOG:BAD_N:")
        return

    with log_lock:
        tail = log_buf[-n:] if n > 0 else []

    send_line(sock, "LOGBEGIN:")
    for ln in tail:
        send_line(sock, f"LOGENTRY:{ln}:")
    send_line(sock, "LOGEND:")
    send_line(sock, "OK:LOG:")


def handle_bye(sock, parts):
    # BYE:SID:
    if len(parts) < 2:
        send_line(sock, "FAIL:BYE:FORMAT:")
        return
    sid = parts[1]
    sess = auth_required(sock, sid)
    if not sess:
        return
    agent_id = sess["agent"]

    with agents_lock:
        agents.pop(agent_id, None)
    with sessions_lock:
        sessions.pop(sid, None)

    send_line(sock, "OK:BYE:")
    log_event(f"[BYE] agent={agent_id}")


def process_line(sock, line):
    parts = line.split(":")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    code = parts[0] if parts else ""
    if not code:
        return

    if code == "HELLO":
        handle_hello(sock, parts)
    elif code == "RESPONSE":
        handle_response(sock, parts)
    elif code == "PING":
        handle_ping(sock, parts)
    elif code == "LIST":
        handle_list(sock, parts)
    elif code == "DM":
        handle_dm(sock, parts)
    elif code == "BCAST":
        handle_bcast(sock, parts)
    elif code == "ACK":
        handle_ack(sock, parts)
    elif code == "ONCE":
        handle_once(sock, parts)
    elif code == "READ":
        handle_read(sock, parts)
    elif code == "LOCK":
        handle_lock(sock, parts)
    elif code == "LOG":
        handle_log(sock, parts)
    elif code == "BOOK_SHOW":
        handle_book_show(sock, parts)
    elif code == "BOOK_ADD":
        handle_book_add(sock, parts)
    elif code == "BOOK_SET":
        handle_book_set(sock, parts)
    elif code == "BOOK_DEL":
        handle_book_del(sock, parts)
    elif code == "BOOK_PASS":
        handle_book_pass(sock, parts)
    elif code == "BOOK_LEVEL":
        handle_book_level(sock, parts)
    elif code == "BYE":
        handle_bye(sock, parts)
    else:
        send_line(sock, "FAIL:UNKNOWN_CODE:")


def client_thread(sock, addr):
    log_event(f"[CONNECT] {addr}")
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            for line in parse_lines(sock, data):
                process_line(sock, line)
    except Exception as e:
        log_event(f"[ERROR] {addr} {e}")
    finally:
        with chal_lock:
            challenges.pop(sock, None)
        remove_agent_by_sock(sock)
        with buf_lock:
            sock_buffers.pop(sock, None)
        try:
            sock.close()
        except:
            pass
        log_event(f"[DISCONNECT] {addr}")


def main():
    ensure_default_book_file()
    load_book()

    serverSock = socket(AF_INET, SOCK_STREAM)
    serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSock.bind((HOST, PORT))
    serverSock.listen(5)

    print(f"[SERVER] listening on {HOST}:{PORT}")
    print(f"[BOOK] loaded from {BOOK_FILE} (agents={len(AGENT_BOOK)})")

    while True:
        clientSock, addr = serverSock.accept()
        threading.Thread(target=client_thread, args=(clientSock, addr), daemon=True).start()


if __name__ == "__main__":
    main()