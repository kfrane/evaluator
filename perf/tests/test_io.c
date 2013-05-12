#include <stdio.h>

char word[1024];

int main() {
  while(1) {
    int ret = scanf("%s", word);
    if (ret == EOF) break;
    printf("%s\n", word);
  }
  return 0;
}
