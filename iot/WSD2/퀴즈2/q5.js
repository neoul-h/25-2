
let fruits = ['귤', '레몬', '사과', '수박', '바나나', '복숭아', '자두', '파인애플'];
console.log(fruits.slice(2, 5).splice(1, 3).reduce((acc, item) => acc += item.length, 0));