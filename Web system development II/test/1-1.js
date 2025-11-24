// 1-1.js
// 목표: Node 이벤트 루프( nextTick → check(setImmediate) → timers(setTimeout) ) 순서에 따라
//       v 값이 어떻게 변하는지 확인하고, 2초 뒤 최종 값을 출력한다.

let v = 0; // 시작값

// (A) 1000ms 후에 v += 1 (타이머 A)
//     - timers 단계(약 1초 후)에서 실행
setTimeout(() => { v += 1; /* A: +1 */ }, 1000);

// (B) setImmediate는 같은 루프의 poll 뒤, check 단계에서 실행
//     - 여기서는 v *= 2
setImmediate(() => { v *= 2; /* B: ×2 */ });

// (C) process.nextTick은 "동기 코드 직후" 가장 먼저 실행되는 마이크로태스크 큐
//     - 이 콜백 안에서 타이머/즉시 실행을 추가 등록하고, 즉시 v += 3도 수행
process.nextTick(() => {
  // (C-1) 1000ms 후에 v /= 2 (타이머 D)
  setTimeout(() => { v /= 2; /* D: ÷2 */ }, 1000);

  // (C-2) 같은 루프의 check 단계에서 v -= 3 (즉시 실행 E)
  setImmediate(() => { v -= 3; /* E: −3 */ });

  // (C-3) nextTick 콜백 본문: 즉시 v += 3
  v += 3; // 0 → 3
});

// (D) 2000ms 후에 최종 v를 출력
setTimeout(() => console.log(v), 2000);

/*
[짧은 타임라인]
t≈0ms  : nextTick(C-3) → v=3
         check: B(×2) → 6, E(−3) → 3
t≈1000ms: timers: A(+1) → 4, D(÷2) → 2
t≈2000ms: log → 2

[예상 출력]
2
*/
