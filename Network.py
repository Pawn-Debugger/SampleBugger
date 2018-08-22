import socket
import select
import struct
import threading

from proto.task_pb2 import Task;
from proto.response_pb2 import Response;

class DebuggerOfflineException(Exception):
  pass

class Network:
  socket = None
  connected = False
  breakpoint_listener_thread = None
  cancel_breakpoint_listener = threading.Event()

  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      self.connect()
    except DebuggerOfflineException:
      print("Debugger is offline, will retry when required")

  def connect(self):
    if self.connected:
      return

    print("Connecting to debugger")

    attempt = 0
    while attempt < 3:
      try:
        self.socket.connect(('127.0.0.1', 7667))
        self.connected = True
        print("Connected to debugger")
        return
      except ConnectionRefusedError as e:
        attempt += 1
        print(f"Failed to connect (attempt {attempt})")

    raise DebuggerOfflineException()

  def send(self, data):
    try:
      self.socket.sendall(data)
    except (ConnectionAbortedError, ConnectionResetError) as e:
      self.socket.close()
      self.connect()
      self.send(data)
    except OSError as e:
      if e.args[0] == 10054:
        self.socket.close()
      elif e.args[0] != 10057:
        raise
      self.connect()
      self.send(data)

  def query_registers(self):
    task = Task()
    task.type = Task.QUERY_REGISTERS

    response = self.send_task(task)
    return response.registers

  def run(self):
    task = Task()
    task.type = Task.RUN

    response = self.send_task(task)
    if response.type == Response.SUCCESS:
      self.await_breakpoint()
      return True
    else:
      return False

  def step_single(self):
    task = Task()
    task.type = Task.STEP_SINGLE

    response = self.send_task(task)
    return response.registers

  def step_line(self):
    task = Task()
    task.type = Task.STEP_LINE

    response = self.send_task(task)
    return response.registers

  def breakpoint_line_add(self, file, line):
    return response.registers

  def breakpoint_cip_add(self, cip):
    task = Task()
    task.type = Task.BREAKPOINT_ADD
    task.breakpoint.instruction_pointer = cip

    # In this sample debugger we have to wait for answer immediately due to lack of threading
    response = self.send_task(task)
    return response.registers

  def breakpoint_cip_remove(self, cip):
    task = Task()
    task.type = Task.BREAKPOINT_REMOVE
    task.breakpoint.instruction_pointer = cip

    response = self.send_task(task)
    return response.registers    

  def query_memory(self, offset, length):
    task = Task()
    task.type = Task.QUERY_MEMORY
    task.memory_query.offset = offset
    task.memory_query.length = length

    response = self.send_task(task)
    return response.memory_region

  def send_task(self, task):
    was_awaiting = False
    if self.breakpoint_listener_thread:
      was_awaiting = True
      self.stop_awaiting_breakpoints()

    packet = task.SerializeToString()
    size = struct.pack('>I', len(packet))
    self.send(size)
    self.send(packet)
    response = self.read_response()

    if was_awaiting:
      self.await_breakpoint()

    return response

  def read_response(self):
    data = self.socket.recv(4)
    if data == b'':
      raise DebuggerOfflineException()

    size = struct.unpack('>I', data)[0]
    pbbytes = self.socket.recv(size)
    response = Response()
    response.ParseFromString(pbbytes)
    return response

  def await_breakpoint(self):
    self.breakpoint_listener_thread = threading.Thread(target=self._await_breakpoint)
    self.breakpoint_listener_thread.start()

  def _await_breakpoint(self):
    while not self.cancel_breakpoint_listener.is_set():
      r, _, _ = select.select([self.socket], [], [], 0.25)
      if r:
        print("Got a breakpoint!")
        self.read_response()

    self.cancel_breakpoint_listener.clear()

  def stop_awaiting_breakpoints(self):
    self.cancel_breakpoint_listener.set()
    self.breakpoint_listener_thread.join()
    self.breakpoint_listener_thread = None