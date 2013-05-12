#!/usr/bin/python3

import lxc
import os
import sys
import shutil
import getopt

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

def main():
  # some configs
  container_name = 'sandbox'
  container_paths = '/var/lib/lxc/'
  rootfs = container_paths + container_name + '/rootfs'

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

  tmp_path = rootfs + '/tmp'
  cmd_in_container = '/tmp/' + copy_if_needed(cmd_to_run, tmp_path)
  print ("Cmd in container", cmd_in_container)
  container.attach('ALL', cmd_in_container, *cmd_params)

  print('Immediately after attach')
  container.stop()

if __name__ == "__main__":
  main()
