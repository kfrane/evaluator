CC = gcc
C_FLAGS = -Wall

all: perf perf_tests

perf: perf.c
	$(CC) perf.c -operf $(C_FLAGS)

perf_tests: tests/core_dump_create tests/dofork tests/forkbomb tests/test_io

tests/core_dump_create: tests/core_dump_create.c
	$(CC) tests/core_dump_create.c -otests/core_dump_create $(C_FLAGS)

tests/dofork: tests/dofork.c
	$(CC) tests/dofork.c -otests/dofork $(C_FLAGS)

tests/forkbomb: tests/forkbomb.c
	$(CC) tests/forkbomb.c -otests/forkbomb $(C_FLAGS)

tests/test_io: tests/test_io.c
	$(CC) tests/test_io.c -otests/test_io $(C_FLAGS)

clean:
	rm perf tests/core_dump_create tests/dofork tests/forkbomb tests/test_io
