let v = 1;

let id = setImmediate(() => console.log(3));

new Promise(resolve => {
    setImmediate(() => console.log(6));
    resolve();
    setTimeout(() => {
       console.log(9) 
    }, timeout);
}).then(() => setImmediate(() => console.log(8)));

setImmediate(() => console.log(10));