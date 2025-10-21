



let v = 0;

const k1 = setInterval(() => v += 1, 100);
const k2 = setInterval(() => v -= 1, 300);

const promise = new Promise(resolve => {

resolve();
process.nextTick(() => v *= 2);
v += 2;
})
.then (() => {
clearInterval(k1);
v += 2;
return new Promise(resolve => setTimeout(()=> resolve(), 500));
})
.then (() => {
clearInterval(k2)
v += 2;
})

.finally(() => v /=2);

setTimeout(() => console.log(v), 2000);