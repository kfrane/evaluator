#!/usr/bin/python3

import mylxc
from attach import Attach
from monitor_mem import MonitorMem
import os
import sys
import shutil
import getopt
import threading
import time
from ctypes import c_longlong

class Evaluator:
  def __init__(self):
    # some configs
    self.container_name = 'sandbox'
    self.container_paths = '/var/lib/lxc/'
    self.rootfs = self.container_paths + self.container_name + '/rootfs'
    self.cgroup_path = '/sys/fs/cgroup/memory/lxc/' + self.container_name + '/'

  def copy_if_needed(source, dest):
    last_slash = source.rfind('/')
    filename = source[last_slash+1:]
    if dest[len(dest)-1] != '/':
      dest += '/'
    dest += filename
    if os.path.isfile(dest): # already exists
      return filename
    try:
      shutil.copy(source, dest)
    except FileNotFoundError as why:
      print("Couldn't copy file", why)
      sys.exit(1)
    return filename

  def force_kill(self):
    print("Attempting force kill")
    prev_pid = None
    while self.container.running:
      init_pid = self.container.init_pid
      if (init_pid is None) or (init_pid <= 0):
        break
      if init_pid == prev_pid:
        # if the process isn't killed we will give it 100 ms before another kill
        time.sleep(0.1)
        prev_pid = None
        continue
      if init_pid <= 1:
        return
      try:
        os.kill(init_pid, signal.SIGKILL)
      except:
        pass
      prev_pid = init_pid

  def set_memory_limits(self, memory_limit):
    cgroup_mem = ['memory.limit_in_bytes', 'memory.memsw.limit_in_bytes']
    for limit in cgroup_mem:
      if memory_limit == None:
        break
      if self.container.set_cgroup_item(limit, memory_limit) == False:
        print(container.get_cgroup_item(limit))
        print("Aborting, couldn't set memory limits for container.")
        self.container.stop()
        sys.exit(1)

  def absoulute_stop(self):
    """
    This will definetively stop self.container,
    and will block until it is stopped.
    """
    self.container.stop()
    self.container.wait("STOPPED", 1)
    if self.container.running:
      self.force_kill()

  def evaluate(self, memory_limit, time_limit, cmd_to_run, cmd_params):
    # parse command line args
    # memory_limit, time_limit, cmd_to_run, cmd_params = parse_args()
    self.container = mylxc.MyContainer(self.container_name)
    if self.container.state != 'STOPPED':
      print ("self.container", self.container_name,"is already running.")
      return
    self.container.start()
    self.container.wait("RUNNING", 1)
    if self.container.state != 'RUNNING':
      self.container.stop()
      print ("self.container", self.container_name, "won't run")
      return
    self.set_memory_limits(memory_limit)

    thread_exited = threading.Event()
    # monitor will notify 1M before actual limit,
    # because it sometimes notifies too late
    monitor = MonitorMem(
      self.cgroup_path,
      int(memory_limit) - 1024 * 1024,
      thread_exited)
    monitor.start()

    tmp_path = self.rootfs + '/tmp'
    cmd_in_container = '/tmp/' + Evaluator.copy_if_needed(cmd_to_run, tmp_path)
    attach_thread = Attach(
      self.container,
      cmd_in_container,
      cmd_params,
      thread_exited)
    attach_thread.start()

    if time_limit == None: # there is no time limit!
      thread_exited.wait()
    else:
      thread_exited.wait(float(time_limit) / 1000.0)

    memory_limit_exceeded = False
    time_limit_exceeded = False
    time_elapsed = None
    if attach_thread.start_time is not None:
       time_elapsed = time.time() - attach_thread.start_time
    # At least one thread has stopped.
    if not thread_exited.isSet():
      # timeout happend, and self.container must be stopped,
      # because time limit has exceeded
      time_limit_exceeded = True
    elif monitor.exited:
      # memory limit exceeded
      memory_limit_exceeded = True
    else:
      # program exited normally
      pass
    self.absoulute_stop()

    results = open('results.txt', 'w')
    results.write(str(time_limit_exceeded) + '\n')
    results.write(str(time_elapsed) + '\n')
    results.write(str(memory_limit_exceeded) + '\n')
    results.write(str(attach_thread.ret) + '\n')
    results.close()


def parse_args():
  memory_limit = None
  time_limit = None
  try:
    opts, args = getopt.getopt(sys.argv[1:], "+m:c:")
    if len(args) == 0:
      raise getopt.GetoptError("No cmd to execute.")
    for opt, val in opts:
      if opt == '-m':
        memory_limit = val
      elif opt == '-c':
        time_limit = val
      else:
        raise getopt.GetoptError("Unknown option " + opt + "received.")
  except getopt.GetoptError as err:
    print(err)
    print("Usage: evaluator [-m virtual memory limit]"
        + " [-c cpu time limit in miliseconds] user_prog user_params\n"
        + "-m nonnegative number (default is no limit)\n"
        + "-c positive number (default is no limit)\n")
    sys.exit(1)
  return (memory_limit, time_limit, args[0], args[1:])

def main():
  memory_limit, time_limit, cmd_to_run, cmd_params = parse_args()
  evaluator = Evaluator()
  evaluator.evaluate(memory_limit, time_limit, cmd_to_run, cmd_params)

if __name__ == "__main__":
  main()
