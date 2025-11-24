// 3-3.js
// 목표: CommonJS 환경에서 require.main, module.exports, exports, this 관계 확인
// 주의: & 는 논리 AND(&&)가 아닌 "비트 AND" — true/false가 각각 1/0으로 변환되어 계산됨

// 이 파일을 "직접 실행"할 때 보통 다음이 성립:
// - require.main === module  → require.main.exports === module.exports → true
// - 최상위 스코프에서 exports === this → true (CommonJS 래퍼 함수의 this가 exports를 가리킴)
//
// 따라서 true & true → 1 & 1 → 1 출력
// (만약 이 파일을 다른 파일에서 require로 불러 실행하면, require.main !== module 이라 첫 비교가 false가 될 수 있음)

console.log(require.main.exports === module.exports & exports === this);

/*
[예상 출력] (직접 실행 시)
1
*/
