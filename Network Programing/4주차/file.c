#include <stdio.h>

int main(void)
{
  int x, y, pre, post;
  x = 1;
  y = 1;
  printf("x=%d y=%d\n", x, y);
  pre = ++x;                                      
  /* 
  1. x = ?  -> x = 1 (위에 선언 됨)
  2. ++x = ? -> ++x 란 x값이 증가한 x의 값이다 -> ++x 란 증가 수식이 있다. -> x = x + 1 이다.
  3. ++x 는 이미 pre = ++x; 여기서 x = 1 인 상태에서 ++x에 의해 x = 2 이고 그 후에 ++x = 2 인데 ++x = pre래요
  그려서 결과적으로 pre = 2 이며 x 의 값도 2 가 된다  
  */
  post = y++;                                     
  printf("pre=%d post=%d\n", pre, post);
  printf("x=%d y=%d\n", x, y);
  return 0;
}