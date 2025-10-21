/*
1.제어권 잃어버리는 모델 = 블로킹
2.노드 서버 장단점이 아닌것 = CPU 작업 많 작업 적합 
3.Event loop는 node.js의 *main* thread이다
4.HTTP 상태 코드 중 임시 이동을 의미하는 코드 = 302

이걸 외우면 안되고 관련된걸 싹 다 외우자

*/

// 문제 5번

let v = 0;
setTimeout(() => setInterval(()=> v +=1,1500),1000);

const promise = new Promise(resolve => {
    queueMicrotask(() => setTimeout(() => resolve(), 1500));

})

.then(() => v += 5)
.then(() => v*= 2)

setTimeout(() => console.log(v), 7000);
