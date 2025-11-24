// 1-3.js
// 목표: (1) 같은 이름의 함수 선언이 2개일 때 "마지막 선언"이 호이스팅으로 최종 본체가 됨
//       (2) I/O 콜백 내부에서 예약하면 setImmediate 가 setTimeout(..., 0)보다 먼저 실행되는 순서 확인

let i = 1;

/*
⚠️ 같은 이름의 f가 아래에 한 번 더 선언되어 있음
→ 함수 선언은 '호이스팅'되며, "마지막 선언"이 최종적으로 적용됨
→ 따라서 아래의 f(); 호출도 사실상 "두 번째 f"를 호출하게 됨
*/
function f() {
  // (구버전 본문) 실제로는 호출되지 않음(아래 f가 덮어씀)
  setTimeout(() => { i += 5; /* 사용되지 않음 */ }, 0);
  setImmediate(() => { i *= 5; /* 사용되지 않음 */ });
}

// f() 호출 → 호이스팅 덕분에 "두 번째 f"가 실행됨
f();

// 100ms 뒤 현재 i 값을 출력
setTimeout(() => console.log(i), 100);

/*
✅ 실제로 적용되는 f (호이스팅으로 이 본문이 유효)
- fs.readFile('', cb): 잘못된 경로로 읽기를 시도하므로 에러와 함께 비동기 콜백 호출
- "I/O 콜백(poll 단계)" 안에서 setImmediate 와 setTimeout(0) 을 예약하면,
  같은 루프의 check 단계에서 setImmediate 가 먼저, 그 다음 틱의 timers 단계에서 setTimeout(0)이 실행됨
*/
function f() {
  const fs = require('fs');
  fs.readFile('', _err => {
    // I/O 콜백 내부에서 예약:
    setTimeout(() => { i *= 2; /* T0: 다음 틱 timers 단계 */ }, 0);
    setImmediate(() => { i += 2; /* C0: 같은 틱 check 단계 */ });
  });
}

/*
[짧은 타임라인]
t≈0ms   : f() → 실제로는 두 번째 f → readFile 비동기 등록
t≈다음틱: poll 단계에서 I/O 콜백 실행 → setImmediate(+2), setTimeout(×2, 0) 예약
         check: +2 → i: 1→3
t≈그다음틱 timers: ×2 → i: 3→6
t≈100ms : log → 6

[예상 출력]
6
*/
