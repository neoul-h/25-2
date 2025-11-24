// 3-1.js (수정본) — 복붙 실행용 주석 버전
// 목표:
//  1) 인터벌 k1(200ms, -1), k2(100ms, +1), k3(250ms, resolve)와
//  2) Promise 체인(then → reject(100ms 지연) → catch → finally)의 상호작용,
//  3) 500ms 시점에서 setTimeout(log)과 k3의 2회차(=500ms)가 동시에 만료될 때
//     "등록 순서" 때문에 log가 먼저 실행되어 k3를 끊는 흐름을 확인한다.

let v = 0;

// (k1) 200ms마다 v -= 1
const k1 = setInterval(() => v -= 1, 200);

// (k2) 100ms마다 v += 1
const k2 = setInterval(() => v += 1, 100);

let k3; // 250ms마다 resolve()를 시도할 인터벌 핸들

// (1) 새 Promise: executor에서 k3를 시작한다.
//     k3는 250ms마다 resolve() 콜백을 호출 → 첫 resolve는 t≈250ms에 발생한다.
const promise = new Promise(resolve =>
  k3 = setInterval(() => resolve(), 250)
)
// (2) 첫 then: t≈250ms에 실행됨(마이크로태스크).
//     여기서 k1(−1 인터벌)을 즉시 해제하고,
//     100ms 뒤에 reject시키는 Promise를 "반환"하여 다음 체인을 실패로 보낸다.
.then(() => {
  clearInterval(k1); // 이제부터 v -= 1은 더 이상 발생하지 않음
  return new Promise((_, reject) => setTimeout(() => reject(), 100)); // t≈350ms에 reject
})
// (3) 위 then이 "reject"되므로 이 then은 건너뛴다(실행되지 않음).
.then(() => v += 5)
// (4) catch: t≈350ms에 실행. 여기서 k2(+1 인터벌)를 해제한다.
.catch(() => clearInterval(k2))
// (5) finally: catch 이후 즉시 실행. v *= 2로 마무리.
.finally(() => v *= 2);

// (6) 500ms에 k3를 끊고 현재 v를 출력.
//     동일 500ms에 k3의 2회차도 만료되지만,
//     이 setTimeout(500)은 t=0에 등록되었고,
//     k3(2회차=500ms)는 t=250에 재등록되었으므로 등록 순서상 setTimeout이 먼저 실행된다.
setTimeout(() => {
  clearInterval(k3); // 두 번째 resolve 호출 전에 인터벌을 끊는다.
  console.log(v);    // 최종 v 출력
}, 500);

/*
──────────────────── 타임라인 (값 변화 중심) ────────────────────
초기: v = 0

t=100ms : k2(+1)        → v: 0 → 1
t=200ms : k1(−1)        → v: 1 → 0
         k2(+1)         → v: 0 → 1
t=250ms : k3 resolve    → (then 실행) clearInterval(k1)
                         → 100ms 뒤(reject 타이머) 예약
t=300ms : k2(+1)        → v: 1 → 2    // k1은 이미 중단됨
t=350ms : reject 타이머 → (catch) clearInterval(k2) → k2 중단
                         → (finally) v *= 2 → v: 2 → 4
t=500ms : setTimeout    → clearInterval(k3); log(v=4)
         (동시간 k3 2회차는 setTimeout이 먼저 실행되어 끊김)

[예상 출력]
4
*/
