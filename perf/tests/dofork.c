#include <unistd.h>
#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <err.h>

void printID() {
  printf("Real uid %d\n", getuid());
  printf("Effective uid %d\n", geteuid());
}

int main(int argc, char *argv[]) {
  struct rlimit thread_limits;

  int child_pid = fork();
  if (child_pid == -1) { // child
    err(1, "Fork isn't working\n");
  }
  if (child_pid != 0) { // parent
    int st;
    waitpid(child_pid, &st, 0);
    printf ("child has finised with status %d\n", st);
  }
  printID();
  getrlimit(RLIMIT_NPROC, &thread_limits);
  printf("Thread limits %lu %lu\n", thread_limits.rlim_cur, thread_limits.rlim_max);
  return 0;
}
