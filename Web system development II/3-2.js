// 3-2.js
// 목표: nextTick vs Promise(.then) 우선순위, 인터벌 해제 타이밍, 최종 값 계산
// 핵심: Node에선 process.nextTick이 Promise 마이크로태스크보다 먼저 실행됨

let v = 0;

// (k1) 100ms마다 v += 1
const k1 = setInterval(() => v += 1, 100);

// (k2) 300ms마다 v -= 1
const k2 = setInterval(() => v -= 1, 300);

// (1) Promise executor는 "동기"로 바로 실행됨
const promise = new Promise(resolve => {
  resolve();                  // (1-1) 즉시 해결 → then 콜백이 마이크로태스크 큐에 등록
  process.nextTick(() => v *= 2); // (1-2) nextTick 큐 등록(→ then보다 먼저 실행)
  v += 2;                     // (1-3) 동기: v = 0→2
})
.then(() => {
  // (2) 첫 번째 then: (nextTick 처리 후 실행됨)
  clearInterval(k1); // k1 해제 → 100ms 인터벌은 더 이상 발생하지 않음(즉, k1은 한 번도 못 뛰게 됨)
  v += 2;            // v: 2(→ nextTick 후엔 4) 에서 +2
  // (2-1) 500ms 후에 resolve되는 Promise 반환 → 다음 then은 t≈500ms에 실행
  return new Promise(resolve => setTimeout(() => resolve(), 500));
})
.then(() => {
  // (3) 두 번째 then (t≈500ms)
  clearInterval(k2); // k2 해제
  v += 2;            // +2
})
.finally(() => v /= 2); // (4) 성공/실패와 무관히 마지막에 v /= 2

// (5) 2000ms에 최종값 출력
setTimeout(() => console.log(v), 2000);

/*
[짧은 타임라인]
t≈0ms : 동기 v+=2 → 2
        nextTick: v*=2 → 4
        then(1): clearInterval(k1), v+=2 → 6, 그리고 500ms 대기 Promise 반환
t=300ms: k2 첫 틱 → v: 6→5
t=500ms: then(2): clearInterval(k2), v+=2 → 5→7
         finally: v/=2 → 7→3.5
t=2000ms: log → 3.5

[예상 출력]
3.5
*/
