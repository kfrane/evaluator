#include <stdio.h>
#include <err.h>
#include <unistd.h>

#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>

#define ERR_CODE 117

int thread_limit = -1; // default is no limit on number of threads
long long mem_limit = -1;
int cpu_limit = -1;
int exec_index;

void parse_flags(int argc, char **argv) {
  int ch;
  const char* usage_msg =
    "Usage: mlimit [-t num_threads] [-m virtual memory limit]"
    " [-c cpu time limit in seconds] file_to_execute\n"
    "-t nonnegative number (default is no limit)\n"
    "-m nonnegative number (default is no limit)\n"
    "-c positive number (default is no limit)\n";

  while((ch = getopt(argc, argv, "+t:m:c:")) != -1) {
    switch(ch) {
      case 't': sscanf(optarg, "%d", &thread_limit);
                break;
      case 'm': sscanf(optarg, "%lld", &mem_limit);
                break;
      case 'c': sscanf(optarg, "%d", &cpu_limit);
                break;
      case '?': errx(ERR_CODE, "Unknown option.\n%s", usage_msg);
                break;
      default:  errx(ERR_CODE, "Wrong option.\n%s", usage_msg);

    }
  }
  if (optind >= argc) {
    errx(ERR_CODE, "No cmd to execute.\n%s", usage_msg);
  }
  exec_index = optind;
}

void setlimits(void) {
  struct rlimit coredump_limits, thread_limits, mem_limits, cpu_limits;
  coredump_limits.rlim_cur = coredump_limits.rlim_max = 0;
  if (setrlimit(RLIMIT_CORE, &coredump_limits) != 0) {
    err(ERR_CODE, "Couldn't set core dump limits\n");
  }

  if (thread_limit >= 0) {
    thread_limits.rlim_cur = thread_limits.rlim_max = thread_limit;
    if (setrlimit(RLIMIT_NPROC, &thread_limits) != 0) {
      err(ERR_CODE, "Couldn't set thread limits\n");
    }  
  }

  if (mem_limit >= 0) {
    mem_limits.rlim_cur = mem_limits.rlim_max = mem_limit;
    if (setrlimit(RLIMIT_AS, &mem_limits) != 0) {
      err(ERR_CODE, "Couldn't set mem limits\n");
    }  
  }

  if (cpu_limit >= 0) {
    cpu_limits.rlim_cur = cpu_limits.rlim_max = cpu_limit;
    if (setrlimit(RLIMIT_CPU, &cpu_limits) != 0) {
      err(ERR_CODE, "Couldn't set cpu limits\n");
    }  
  }


  getrlimit(RLIMIT_NPROC, &thread_limits);
}

double time_to_double(const struct timeval ru_utime) {
  return (double)ru_utime.tv_sec  + (double)ru_utime.tv_usec / (double)1000000;
}

int main(int argc, char *argv[]) {
  int i;
  int argv_child_len;
  parse_flags(argc, argv);
  
  int fork_ret = fork();
  if (fork_ret < 0) {
    err(1, "Couldn't create child proces.\n");
  } else if (fork_ret == 0) {
    // child process
    int setuid_ret = setuid(2789);
    if (setuid_ret < 0) {
      err(setuid_ret, "Couldn't change user id\n");
    }
    setlimits();

    argv_child_len = argc-exec_index;
    char *argv_child[argv_child_len+1];
    for(i = 0; i < argv_child_len; i++) {
      argv_child[i] = argv[exec_index+i];
    }
    argv_child[argv_child_len] = NULL;
    execvp(argv[exec_index], argv_child);
    err(ERR_CODE, NULL);
  } else {
    int status = 0;
    struct rusage child_usage;
    wait4(fork_ret, &status, 0, &child_usage);
    FILE *F_OUT = fopen("results.txt", "w");
    if (F_OUT == NULL) {
      err(ERR_CODE, NULL);
    }
    if (WIFEXITED(status)) {
      fprintf(F_OUT, "%d\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
      fprintf(F_OUT, "%d\n", -WTERMSIG(status));
    } else {
      err(ERR_CODE, NULL);
    }
    fprintf(
        F_OUT,
        "%lf\n%lf\n%ld\n", 
        time_to_double(child_usage.ru_utime),
        time_to_double(child_usage.ru_stime),
        child_usage.ru_maxrss);
    fclose(F_OUT);
  }
  return 0;
}
