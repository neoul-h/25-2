let v = 1;

let id = setInterval(() => v += 3, 1000);
setImmediate(() => v *= 3);

new Promise(resolve => setImmediate(() => resolve(v -= 2)))
.then(v => setTimeout(() => v /= 2, 1000));

setTimeout(() => {
  clearInterval(id);
  console.log(v);
}, 2000);