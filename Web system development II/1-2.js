let v = 0;

const k = setInterval(() => v += 1, 300);

const p = new Promise(resolve => {
  resolve();
  process.nextTick(() => v *= 3);
  v += 2;               // 동기
}).then(() => {
  clearInterval(k);
  v -= 1;
});

setTimeout(() => console.log(v), 1000);
