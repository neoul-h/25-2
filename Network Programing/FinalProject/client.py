from socket import *
import threading
import sys
import time
import base64

HOST = "127.0.0.1"
PORT = 6000

SID = None
LEVEL = None
SHIFT = 0
AGENT = None

msg_counter = 1
recv_buf = ""
ENC_ON = True


def b64_enc(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def b64_dec(s: str) -> str:
    return base64.b64decode(s.encode()).decode()


def caesar_shift(text, shift):
    out = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            out.append(chr((o - 65 + shift) % 26 + 65))
        elif 97 <= o <= 122:
            out.append(chr((o - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def enc_payload(plain):
    if not ENC_ON:
        return plain
    return caesar_shift(plain, SHIFT)


def dec_payload(cipher):
    if not ENC_ON:
        return cipher
    return caesar_shift(cipher, (-SHIFT) % 26)


def make_proof(agent_id, nonce):
    return str(nonce)[::-1] + "-" + str(len(agent_id))


def send_line(sock, line):
    if not line.endswith("\n"):
        line += "\n"
    sock.sendall(line.encode())


def parse_lines(data_bytes):
    global recv_buf
    text = data_bytes.decode(errors="ignore")
    recv_buf += text
    lines = recv_buf.split("\n")
    recv_buf = lines[-1]
    return [ln.strip() for ln in lines[:-1] if ln.strip()]


def next_msg_id():
    global msg_counter
    mid = f"MSG{msg_counter:04d}"
    msg_counter += 1
    return mid


def prompt(ui):
    if ui["mode"] == "BCAST":
        return "ALL> "
    if ui["mode"] == "DM":
        return f'{ui["target"]}> ' if ui["target"] else "DM(상대ID)> "
    return "> "


def redraw_prompt(ui):
    print("\r" + prompt(ui), end="", flush=True)


def heartbeat(sock):
    while True:
        time.sleep(10)
        if SID:
            try:
                send_line(sock, f"PING:{SID}:")
            except:
                break


def recv_thread(sock, ui):
    global SID, LEVEL, SHIFT, ENC_ON
    in_book = False
    in_log = False

    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break

            for line in parse_lines(data):
                parts = line.split(":")
                if parts and parts[-1] == "":
                    parts = parts[:-1]
                code = parts[0] if parts else ""

                if code == "CHALLENGE":
                    nonce = int(parts[1]) if len(parts) > 1 else 0
                    proof = make_proof(AGENT, nonce)
                    send_line(sock, f"RESPONSE:{AGENT}:{proof}:")
                    continue

                if code == "PONG":
                    # 조용히 무시 (화면 안 어지럽게)
                    continue

                if code == "AUTH_OK":
                    SID = parts[1] if len(parts) > 1 else None
                    LEVEL = int(parts[2]) if len(parts) > 2 else 1
                    SHIFT = int(parts[3]) if len(parts) > 3 else 0
                    sys.stdout.write(f"\r(인증 성공) SID={SID}, LEVEL={LEVEL}, SHIFT={SHIFT}, ENC={'ON' if ENC_ON else 'OFF'}\n")
                    redraw_prompt(ui)
                    continue

                if code == "AUTH_FAIL":
                    reason = parts[1] if len(parts) > 1 else ""
                    sys.stdout.write(f"\r(인증 실패) {reason}\n")
                    sys.stdout.flush()
                    continue

                if code == "AGENTS":
                    ids = parts[1] if len(parts) > 1 else ""
                    sys.stdout.write("\r[접속 요원]\n")
                    if ids:
                        for a in ids.split(","):
                            sys.stdout.write(f"  - {a}\n")
                    else:
                        sys.stdout.write("  (없음)\n")
                    redraw_prompt(ui)
                    continue

                if code == "DELIVER_BCAST":
                    frm = parts[1] if len(parts) > 1 else "?"
                    mid = parts[2] if len(parts) > 2 else "?"
                    payload_b64 = parts[3] if len(parts) > 3 else ""
                    payload = b64_dec(payload_b64)
                    sys.stdout.write(f"\r[ALL] {frm} ({mid}) > {dec_payload(payload)}\n")
                    if SID:
                        send_line(sock, f"ACK:{SID}:{mid}:")
                    redraw_prompt(ui)
                    continue

                if code == "DELIVER_DM":
                    frm = parts[1] if len(parts) > 1 else "?"
                    mid = parts[2] if len(parts) > 2 else "?"
                    payload_b64 = parts[3] if len(parts) > 3 else ""
                    payload = b64_dec(payload_b64)
                    sys.stdout.write(f"\r[DM] {frm} ({mid}) > {dec_payload(payload)}\n")
                    if SID:
                        send_line(sock, f"ACK:{SID}:{mid}:")
                    redraw_prompt(ui)
                    continue

                if code == "ACK_DONE":
                    mid = parts[1] if len(parts) > 1 else "?"
                    kind = parts[2] if len(parts) > 2 else ""
                    sys.stdout.write(f"\r(ACK 완료) {mid} [{kind}]\n")
                    redraw_prompt(ui)
                    continue

                if code == "ONCE_NOTICE":
                    frm = parts[1] if len(parts) > 1 else "?"
                    mid = parts[2] if len(parts) > 2 else "?"
                    sys.stdout.write(f"\r(1회성 메시지 도착) from={frm}, msg_id={mid}  → /READ {mid}\n")
                    redraw_prompt(ui)
                    continue

                if code == "DELIVER_ONCE":
                    frm = parts[1] if len(parts) > 1 else "?"
                    mid = parts[2] if len(parts) > 2 else "?"
                    payload_b64 = parts[3] if len(parts) > 3 else ""
                    payload = b64_dec(payload_b64)
                    sys.stdout.write(f"\r[ONCE] {frm} ({mid}) > {dec_payload(payload)}\n")
                    redraw_prompt(ui)
                    continue

                if code == "DESTROYED":
                    mid = parts[1] if len(parts) > 1 else "?"
                    sys.stdout.write(f"\r(자폭 완료) msg_id={mid}\n")
                    redraw_prompt(ui)
                    continue

                if code == "REKEY_OK":
                    new_shift = int(parts[1]) if len(parts) > 1 else 0
                    SHIFT = new_shift
                    sys.stdout.write(f"\r(키 재발급) SHIFT={SHIFT}\n")
                    redraw_prompt(ui)
                    continue

                if code == "LOGBEGIN":
                    in_log = True
                    sys.stdout.write("\r[서버 로그]\n")
                    continue

                if code == "LOGENTRY" and in_log:
                    entry = parts[1] if len(parts) > 1 else ""
                    sys.stdout.write(f"  {entry}\n")
                    continue

                if code == "LOGEND":
                    in_log = False
                    redraw_prompt(ui)
                    continue

                if code == "BOOKBEGIN":
                    in_book = True
                    sys.stdout.write("\r[코드북]\n")
                    continue

                if code == "BOOKENTRY" and in_book:
                    aid = parts[1] if len(parts) > 1 else ""
                    pw = parts[2] if len(parts) > 2 else ""
                    lv = parts[3] if len(parts) > 3 else ""
                    sys.stdout.write(f"  - {aid}  {pw}  L{lv}\n")
                    continue

                if code == "BOOKEND":
                    in_book = False
                    redraw_prompt(ui)
                    continue

                if code == "OK":
                    action = parts[1] if len(parts) > 1 else ""
                    sys.stdout.write(f"\r(성공: {action})\n")
                    redraw_prompt(ui)
                    continue

                if code == "FAIL":
                    action = parts[1] if len(parts) > 1 else ""
                    reason = parts[2] if len(parts) > 2 else ""
                    sys.stdout.write(f"\r(실패: {action} / {reason})\n")
                    redraw_prompt(ui)
                    continue

                sys.stdout.write(f"\r(수신) {line}\n")
                redraw_prompt(ui)

        except:
            break

    print("\n[알림] 서버 연결 종료")


def main():
    global AGENT, ENC_ON

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((HOST, PORT))
    print(f"(서버 접속) {HOST}:{PORT}")

    AGENT = input("요원 ID 입력: ").strip()
    passcode = input("요원 전용 코드북(passcode) 입력: ").strip()
    if not AGENT or not passcode:
        print("ID/패스코드는 비어 있을 수 없습니다.")
        return

    ui = {"mode": "DM", "target": None}
    threading.Thread(target=recv_thread, args=(sock, ui), daemon=True).start()

    send_line(sock, f"HELLO:{AGENT}:{passcode}:")

    # Heartbeat 시작
    threading.Thread(target=heartbeat, args=(sock,), daemon=True).start()

    print("\n명령어:")
    print("  /LIST                 (L1+)")
    print("  /DM <상대ID>           (L1+)")
    print("  /ALL                  (L3+)")
    print("  /ONCE <상대ID> <내용>  (L2+)")
    print("  /READ <MSG_ID>         (L2+)")
    print("  /ENC ON|OFF            (L1+)")
    print("  /LOCK ON|OFF           (L4)")
    print("  /LOG <N>               (L4)")
    print("  /BYE\n")

    print("코드북 관리(L4 전용):")
    print("  /BOOK                 -> 코드북 전체 보기")
    print("  /BOOK_ADD <id> <pw> <lv(1~4)>")
    print("  /BOOK_SET <id> <pw> <lv(1~4)>")
    print("  /BOOK_DEL <id>")
    print("  /BOOK_PASS <id> <newpw>")
    print("  /BOOK_LEVEL <id> <lv(1~4)>\n")

    while True:
        cmd = input(prompt(ui)).strip()
        if not cmd:
            continue

        if cmd == "/BYE":
            if SID:
                send_line(sock, f"BYE:{SID}:")
            break

        if cmd == "/LIST":
            if not SID:
                print("(아직 인증 전입니다.)")
                continue
            send_line(sock, f"LIST:{SID}:")
            continue

        if cmd == "/ALL":
            ui["mode"] = "BCAST"
            ui["target"] = None
            print("(전체 방송 모드)")
            continue

        if cmd.startswith("/DM "):
            target = cmd.split(" ", 1)[1].strip()
            if not target:
                print("(사용법) /DM bbb")
                continue
            if target == AGENT:
                print("(자기 자신에게는 DM 불가)")
                continue
            ui["mode"] = "DM"
            ui["target"] = target
            print(f"(DM 모드) 대상={target}")
            continue

        if cmd.startswith("/ENC "):
            val = cmd.split(" ", 1)[1].strip().upper()
            if val not in ("ON", "OFF"):
                print("(사용법) /ENC ON 또는 /ENC OFF")
                continue
            ENC_ON = (val == "ON")
            print(f"(ENC={'ON' if ENC_ON else 'OFF'})")
            continue

        if cmd.startswith("/READ "):
            if not SID:
                print("(아직 인증 전입니다.)")
                continue
            mid = cmd.split(" ", 1)[1].strip()
            send_line(sock, f"READ:{SID}:{mid}:")
            continue

        if cmd.startswith("/ONCE "):
            if not SID:
                print("(아직 인증 전입니다.)")
                continue
            try:
                _, rest = cmd.split(" ", 1)
                to_id, payload_plain = rest.split(" ", 1)
            except:
                print("(사용법) /ONCE bbb 비밀메시지")
                continue
            if to_id == AGENT:
                print("(자기 자신에게는 ONCE 불가)")
                continue

            mid = next_msg_id()
            payload = enc_payload(payload_plain)
            payload_b64 = b64_enc(payload)
            send_line(sock, f"ONCE:{SID}:{to_id}:{mid}:{payload_b64}:")
            continue

        # L4 tools
        if cmd.startswith("/LOCK "):
            if not SID:
                print("(아직 인증 전입니다.)")
                continue
            mode = cmd.split(" ", 1)[1].strip().upper()
            send_line(sock, f"LOCK:{SID}:{mode}:")
            continue

        if cmd.startswith("/LOG "):
            if not SID:
                print("(아직 인증 전입니다.)")
                continue
            n = cmd.split(" ", 1)[1].strip()
            send_line(sock, f"LOG:{SID}:{n}:")
            continue

        # codebook 관리(L4)
        if cmd == "/BOOK":
            send_line(sock, f"BOOK_SHOW:{SID}:")
            continue

        if cmd.startswith("/BOOK_ADD "):
            parts = cmd.split()
            if len(parts) != 4:
                print("(사용법) /BOOK_ADD id pw lv")
                continue
            _, aid, pw, lv = parts
            send_line(sock, f"BOOK_ADD:{SID}:{aid}:{pw}:{lv}:")
            continue

        if cmd.startswith("/BOOK_SET "):
            parts = cmd.split()
            if len(parts) != 4:
                print("(사용법) /BOOK_SET id pw lv")
                continue
            _, aid, pw, lv = parts
            send_line(sock, f"BOOK_SET:{SID}:{aid}:{pw}:{lv}:")
            continue

        if cmd.startswith("/BOOK_DEL "):
            parts = cmd.split()
            if len(parts) != 2:
                print("(사용법) /BOOK_DEL id")
                continue
            _, aid = parts
            send_line(sock, f"BOOK_DEL:{SID}:{aid}:")
            continue

        if cmd.startswith("/BOOK_PASS "):
            parts = cmd.split()
            if len(parts) != 3:
                print("(사용법) /BOOK_PASS id newpw")
                continue
            _, aid, newpw = parts
            send_line(sock, f"BOOK_PASS:{SID}:{aid}:{newpw}:")
            continue

        if cmd.startswith("/BOOK_LEVEL "):
            parts = cmd.split()
            if len(parts) != 3:
                print("(사용법) /BOOK_LEVEL id lv")
                continue
            _, aid, lv = parts
            send_line(sock, f"BOOK_LEVEL:{SID}:{aid}:{lv}:")
            continue

        # 일반 입력: DM/BCAST
        if not SID:
            print("(아직 인증 전입니다.)")
            continue

        mid = next_msg_id()
        payload = enc_payload(cmd)
        payload_b64 = b64_enc(payload)

        if ui["mode"] == "BCAST":
            send_line(sock, f"BCAST:{SID}:{mid}:{payload_b64}:")
        else:
            target = ui["target"]
            if not target:
                print("(먼저 /DM <상대ID> 로 대상 설정)")
                continue
            send_line(sock, f"DM:{SID}:{target}:{mid}:{payload_b64}:")

    try:
        sock.close()
    except:
        pass
    print("클라이언트 종료")


if __name__ == "__main__":
    main()