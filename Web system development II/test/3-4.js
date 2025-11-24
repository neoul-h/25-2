// 3-4.js
// 목표: path.join의 경로 정규화 확인( .. 과 . 처리 )
// OS별 경로 구분자가 다름: POSIX(맥/리눅스)는 '/', Windows는 '\'

const path = require('path');

// 'a', '..'  → 상위로 올라가므로 상쇄
// 'c', '.'   → 그대로 'c' 유지
// 결과적으로 'c'와 'd'가 이어짐
console.log(path.join('a', '..', 'c', '.', 'd'));

/*
[예상 출력]
- POSIX(맥/리눅스): c/d
- Windows        : c\\d
*/
