#include <unistd.h>
#include <stdio.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <err.h>

void printID() {
  printf("Real uid %d\n", getuid());
  printf("Effective uid %d\n", geteuid());
}

int main(int argc, char *argv[]) {
  struct rlimit thread_limits;
  int child_cnt = 0;

  getrlimit(RLIMIT_NPROC, &thread_limits);
  printf("Thread limits %lu %lu\n", thread_limits.rlim_cur, thread_limits.rlim_max);

  while(1) {
    int child_pid = fork();
    if (child_pid == -1) { // child
      err(1, "Fork aint workin', created %d kids\n", child_cnt);
    }
    if (child_pid == 0) { //child sleeps and then dies
      printf("CHILD\n");
      sleep(20);
      return 0;
    }
    child_cnt++;
  }
  return 0;
}
