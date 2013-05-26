import threading
import os
from ctypes import cdll, c_longlong

def eventfd(init_val, flags):
  libc = cdll.LoadLibrary("libc.so.6")
  return libc.eventfd(init_val, flags)


class MonitorMem(threading.Thread):
  def __init__(self, cgroup_path, memory_limit, thread_exited):
    threading.Thread.__init__(self, name = 'Monitornig thread')
    self.exited = False
    self.thread_exited = thread_exited
    self.event_fd = eventfd(0, 0)
    self.memswp_fd = os.open(cgroup_path + 'memory.memsw.usage_in_bytes', os.O_RDONLY)
    self.event_control = open(cgroup_path + 'cgroup.event_control', 'w')
    event_str = str(self.event_fd) + " " + str(self.memswp_fd) + " " + str(memory_limit) + '\n'
    self.event_control.write(event_str)
    self.event_control.flush()

  def run(self):
    self.read_num = os.read(self.event_fd, 8)
    self.read_num_int = 0
    curr_weight = 1
    for i in range(8):
        self.read_num_int += curr_weight * self.read_num[i]
        curr_weight *= 256
    os.close(self.event_fd)
    os.close(self.memswp_fd)
    self.exited = True
    self.thread_exited.set()
