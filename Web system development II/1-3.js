let i = 1;
function f() {
  setTimeout(() => i += 5, 0);  
  setImmediate(() => i *= 5);   
}
f();
setTimeout(() => console.log(i), 100);

function f() { 
  require('fs').readFile('', _ => {
    setTimeout (() => i *= 2, 0);
    setImmediate(() => i += 2);
  }) ;
};