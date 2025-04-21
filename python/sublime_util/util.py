import time

class time_this:
  def __init__(self,txt=''):
    if txt is None:
      self.txt = 'Time: '
    else:
      self.txt = txt+': '

  def __enter__(self,):
    self.start_time = time.time()
    self.start_cpu_time = time.process_time()
    return self

  def __exit__(self, type, value, traceback):
    diff = time.time() - self.start_time
    cpu_diff = time.process_time() - self.start_cpu_time

    s,ms = divmod(diff*1000,1000)
    cs,cms = divmod(cpu_diff*1000,1000)

    print("{}{:.0f}s, {:.0f}ms ({:.0f}s, {:.0f}ms in CPU time)".format(self.txt,s,ms,cs,cms))
