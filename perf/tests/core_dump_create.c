#include <stdio.h>
#include <sys/time.h>
#include <sys/resource.h>

int main() {
  int a;
  struct rlimit limits;
  getrlimit(RLIMIT_CORE, &limits);

  printf(
      "Core dump limits %lu %lu (infinity value is %lu)\n",
      limits.rlim_cur,
      limits.rlim_max,
      RLIM_INFINITY);

  scanf("%d", &a);
  return 4/a;
}
