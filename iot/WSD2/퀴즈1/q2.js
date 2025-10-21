let v = 0;

setTimeout(() => v += 1, 1000);
setImmediate(() => v *= 2);

process.nextTick(() => {
  setTimeout(() => v /= 2, 1000);
  setImmediate(() => v -= 3);
  v += 3;
});

setTimeout(() => console.log(v), 2000);