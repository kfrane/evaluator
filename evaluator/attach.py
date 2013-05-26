import threading
import time

class Attach(threading.Thread):
  def __init__(self, container, cmd_in_container, cmd_params, thread_exited):
    threading.Thread.__init__(self, name = 'Container attach thread')
    self.exited = False
    self.thread_exited = thread_exited
    self.container = container
    self.cmd_in_container = cmd_in_container
    self.cmd_params = cmd_params
    self.ret = None
    self.start_time = None

  def run(self):
    self.start_time = time.time()
    self.ret = self.container.attach(
        'ALL',
        self.cmd_in_container,
        *self.cmd_params)
    self.exited = True
    self.thread_exited.set()
