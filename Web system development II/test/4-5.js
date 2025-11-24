// 4-5.js
// 목표: queueMicrotask + setTimeout(resolve) 타이밍과
//       "setTimeout(7000) 로그" vs "setInterval 1500ms 4회차"의 동시 만료 순서를 확인

let v = 0;

// [A] 1초 뒤에 1.5초 간격 인터벌을 시작한다.
//     → 인터벌 콜백의 최초 실행 시점은 t=1000+1500=2500ms
setTimeout(() => setInterval(() => v += 1, 1500), 1000);

// [B] Promise: executor 안에서 queueMicrotask 등록
//     현재 틱이 끝날 때 이 마이크로태스크가 실행되어 "resolve 타이머(1500ms)"를 예약한다.
//     → 결국 t=1500ms에 resolve 발생
const promise = new Promise(resolve => {
  queueMicrotask(() => setTimeout(() => resolve(), 1500));

})
// resolve 직후(1500ms) 마이크로태스크로 순차 실행
.then(() => v += 5)   // v: 0 → 5
.then(() => v *= 2);  // v: 5 → 10

// [C] 7초 뒤 현재 v를 출력
//     같은 시각에 인터벌 4회차도 만료되지만, 이 로그 타이머가 더 먼저 등록되어 먼저 실행됨.
setTimeout(() => console.log(v), 7000);

// [예상 타임라인 요약]
// t=0    : v=0, 마이크로태스크에서 setTimeout(resolve,1500) 예약
// t=1000 : 인터벌 시작(주기 1500) — 첫 콜백은 t=2500
// t=1500 : then: +5 → 5, 이어서 ×2 → 10
// t=2500 : 인터벌 1회차 +1 → 11
// t=4000 : 인터벌 2회차 +1 → 12
// t=5500 : 인터벌 3회차 +1 → 13
// t=7000 : log 먼저 실행 → 13 출력, 이후 인터벌 4회차가 +1 할 수 있으나 로그 이후라 화면엔 영향 없음

// [예상 출력]
// 13
