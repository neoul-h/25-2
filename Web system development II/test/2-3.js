// 2-3.js
// 주제: var 호이스팅(선언만 끌어올려지고, 초기화는 원래 자리에서 일어남)

var v = 1;

function f() {
  // 함수 스코프 안에서 'var v'가 "선언"만 호이스팅되어
  // 이 시점의 지역 변수 v 값은 'undefined' 상태다.
  console.log(v); // ← undefined 출력

  // 여기서 비로소 지역 변수 v가 2로 "할당"된다.
  var v = 2;
}

f();

/*
[타임라인]
- f 내부 시작 시점: 지역 var v가 선언(호이스팅)되지만 값은 undefined
- console.log(v) → undefined
- 이후 v = 2 할당

[예상 출력]
undefined
*/
