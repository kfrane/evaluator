#!/usr/bin/python3

import lxc
import os
import sys
import shutil
import getopt
import threading
import time

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

start_time = 0
class Attach(threading.Thread):
  def __init__(self, container, cmd_in_container, cmd_params):
    threading.Thread.__init__(self)
    self.container = container
    self.cmd_in_container = cmd_in_container
    self.cmd_params = cmd_params

  def run(self):
    global start_time
    start_time = time.time()
    self.container.attach('ALL', self.cmd_in_container, *self.cmd_params)

def force_kill(container):
  prev_pid = None
  while container.running:
    init_pid = container.init_pid
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

def main():
  # some configs
  container_name = 'sandbox'
  container_paths = '/var/lib/lxc/'
  rootfs = container_paths + container_name + '/rootfs'
  cgroup_mem = ['memory.limit_in_bytes', 'memory.memsw.limit_in_bytes']

  # parse command line args
  memory_limit, time_limit, cmd_to_run, cmd_params = parse_args()
  container = lxc.Container(container_name)
  if container.state != 'STOPPED':
    print ("Container", container_name,"is already running.")
    return
  container.start()
  container.wait("RUNNING", 1)
  if container.state != 'RUNNING':
    container.stop()
    print ("Container", container_name, "won't run")
    return
  print('memory limit', memory_limit)
  for limit in cgroup_mem:
    if memory_limit == None:
      break
    if container.set_cgroup_item(limit, memory_limit) == False:
      print(container.get_cgroup_item(limit))
      print("Aborting, couldn't set memory limits for container.")
      container.stop()
      sys.exit(1)
  ign = input()
  tmp_path = rootfs + '/tmp'
  cmd_in_container = '/tmp/' + copy_if_needed(cmd_to_run, tmp_path)
  print ("Cmd in container", cmd_in_container)
  attach_thread = Attach(container, cmd_in_container, cmd_params)
  attach_thread.start()
  print('Immediately after attach_thead.start()')
  attach_thread.join(float(time_limit) / 1000.0)
  time_elapsed = time.time() - start_time
  time_limit_exceeded = False
  if attach_thread.isAlive():
    time_limit_exceeded = True

  container.stop()
  container.wait("STOPPED", 1)
  if container.running:
    force_kill(container)

if __name__ == "__main__":
  main()
