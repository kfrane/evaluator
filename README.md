evaluator
=========

More details can be found on this blog:
http://sgros-students.blogspot.com/search/label/sandbox

The idea is to create two command line tools. The first one, which is
called evaluator is responsible for running another process in a safe and
confined environment. It will run the untrusted program inside an lxc
container. It is also going to be configurable with parameters such as maximum
allowed memory usage and maximum execution time. These limits refer to the
whole container and not just the untrusted process. This is why the container
will be made to consume the least amount of memory and cpu possible. Its
command line will look like this:

  ./evaluator -m 64000000 -c 2000 ./user_prog user_params

This will run the user_prog inside an lxc container and pass to it all of the
user_params. It will also limit the container's memory usage to 64MB and
execution time to 2000 ms.

The second tool, called perf, is responsible for enforcing some limits on the
untrusted program and also for measuring performance of the untrusted program.
It has similar format of command line as the evaluator:

  ./perf -m 64000000 -c 2000 -t 2 ./user_prog user_params

This will execute file ./user_prog and pass it user_params as command line
arguments. It will limit its memory usage to 64MB, and set time limit of each
thread to 2 seconds and set the allowed number of threads to 2. Perf will also
create file named measurements, which will contain information about how much
memory did the user_prog use, and what was its execution time.

These two tools are intended to be used together, as in the example below:

  ./evaluator -m 65000000 -c 2000 ./perf -t 1 ./user_prog

Evaluator produces results.txt file in its current directory, which gives an overview of the execution. Example is shown below:
True
1.0067088603973389
False
255

First line is True if time limit was exceeded.
Second line is how long did the process run.
Thrid line is True if memory limit was exceeded.
Fourth line is the return code of the user process.
