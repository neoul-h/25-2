// 2-2.js (수정본) — 복붙 실행용 주석 버전
// 목표:
//   1) setImmediate 두 개(×3, resolve(−2))의 실행 순서
//   2) Promise.then 안에서 만든 setTimeout(1000)이 "지역 변수"만 바꾼다는 점
//   3) 2000ms 시점에 setTimeout(log)과 setInterval(2회차)이 동시에 만료될 때
//      "등록 순서" 때문에 log가 먼저 실행되어 인터벌을 끊는다는 점

let v = 1; // 전역 상태 시작값

// (A) 1초마다 v에 +3 하는 인터벌
//     - 1회차: t≈1000ms, 2회차: t≈2000ms, ...
let id = setInterval(() => v += 3, 1000);

// (B) setImmediate는 같은 이벤트 루프 틱의 check 단계에서 실행됨
//     여기서는 먼저 등록된 이 콜백이 "v *= 3"을 수행
setImmediate(() => v *= 3);

// (C) Promise: 실행자(executor)는 동기 실행
//     setImmediate로 resolve(v -= 2)를 등록 → check 단계에서 (B) 이후에 실행됨
new Promise(resolve =>
  setImmediate(() => resolve(v -= 2)) // (B) 다음 순서로 실행되어: v = (1*3)=3 → 3-2=1, resolve(1)
)
// (D) .then의 매개변수 v는 "해결값(=1)"을 받는 **지역 변수**!
//     이 안에서 setTimeout으로 1000ms 뒤에 v /= 2를 해도, 전역 v에는 영향 없음.
.then(v => setTimeout(() => v /= 2, 1000));

// (E) 2000ms에 인터벌을 끊고 전역 v를 출력
setTimeout(() => {
  clearInterval(id); // t≈2000ms에 도착했을 때 인터벌 "2회차"보다 먼저 실행되어 인터벌을 끊는다.
  console.log(v);    // 현재 전역 v를 출력
}, 2000);

/*
──────────────────── 타임라인 (이벤트 루프 단계별) ────────────────────
초기: v = 1

t≈0ms, check 단계:
  (B) v *= 3           : 1 → 3
  (C) resolve(v -= 2)  : 3 → 1, resolve(1) → 마이크로태스크(.then) 실행
      └ .then 에서 setTimeout(지역 v /= 2, 1000) 예약 (전역 v에 영향 없음)

t≈1000ms, timers 단계:
  (A) 인터벌 1회차     : 전역 v += 3 → 1 → 4
  (D) then의 타이머    : 지역 v(해결값) 1 → 0.5 (전역 v 변화 없음)

t≈2000ms, timers 단계(동시 만료 처리 = "등록 순서" 우선):
  (E) setTimeout(log)  : t=0에 등록됨 → 먼저 실행되어 clearInterval(id); log(전역 v=4)
  (A) 인터벌 2회차?     : t=1000에 재등록된 작업. 하지만 위에서 이미 clearInterval로 끊김 → 실행 안 됨

──────────────────────────
[최종 예상 출력]
4
*/
