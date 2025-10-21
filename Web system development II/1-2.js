// 1-2.js
// 목표: nextTick 과 Promise(.then) 우선순위, clearInterval 타이밍에 따른 v 변화 확인
// 핵심: Node에서 process.nextTick 이 Promise 마이크로태스크보다 먼저 비워진다.

let v = 0;

// (A) 300ms마다 v += 1 하는 인터벌 예약
//     - 하지만 곧바로 clearInterval 될 예정이라 실제로는 한 번도 실행되지 않음
const k = setInterval(() => { v += 1; /* 인터벌 증가 */ }, 300);

// (B) Promise executor(실행자)는 "동기"로 즉시 실행됨
const p = new Promise(resolve => {
  resolve();              // (B-1) 즉시 해결 → .then 콜백이 "Promise 마이크로태스크 큐"에 등록
  process.nextTick(() => {
    v *= 3;               // (B-2) nextTick 큐: Promise보다 먼저 실행됨 → 곧 v를 3배로
  });
  v += 2;                 // (B-3) 동기 코드: 즉시 +2 → 0 → 2
}).then(() => {
  // (C) 같은 틱에서 nextTick 처리 후 실행(Promise 마이크로태스크)
  clearInterval(k);       // 인터벌 첫 발사(300ms) 전에 제거 → v += 1은 0회
  v -= 1;                 // 2(×3 후 6)에서 −1 → 5
});

// (D) 1000ms 뒤 최종 v를 출력
setTimeout(() => console.log(v), 1000);

/*
[짧은 타임라인]
t≈0ms  : 동기 v+=2 → 2
         nextTick: v*=3 → 6
         then: clearInterval(k), v−=1 → 5
t≈300ms: 인터벌? 이미 제거 → 변화 없음
t≈1000ms: log → 5

[예상 출력]
5
*/
