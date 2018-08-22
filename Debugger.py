from collections import OrderedDict

class Debugger:
  stopped = True

  registers = OrderedDict({
    "PRI": 0xDEADBEEF,
    "ALT": 0xDEADBEEF,
    "COD": 0xDEADBEEF,
    "DAT": 0xDEADBEEF,
    "HLW": 0xDEADBEEF,
    "HEA": 0xDEADBEEF,
    "STP": 0xDEADBEEF,
    "STK": 0xDEADBEEF,
    "FRM": 0xDEADBEEF,
    "CIP": 0xDEADBEEF
  })

  special_registers = OrderedDict({
    "COD": 0,
    "DAT": 1,
    "HLW": 2,
    "HEA": 3,
    "STP": 4,
    "STK": 5,
    "FRM": 6,
    "CIP": 7
  })

  memory = list()

  def __init__(self, network):
    self.network = network

  def parse_registers(self, new_registers):
    for register in self.registers:
      self.registers[register] = getattr(new_registers, register)

  def query_registers(self):
    if self.stopped:
      print("Machine is stopped, no need to query for register values")

    self.parse_registers(self.network.query_registers())

  def query_memory(self, offset, length):
    if not self.stopped:
      print("Machine is running, the data is volatile")

    self.parse_memory(self.network.query_memory(offset, length), offset, length)

  def parse_memory(self, data, offset, length):
    print(data.cells)

  def run(self):
    if not self.stopped:
      print("Already running")
      return False

    response = self.network.run()
    if response:
      self.stopped = False

    return response

  def stop(self):
    if self.stopped:
      print("Already stopped")
      return False

    print("Screech")

    new_registers = self.network.step_single();
    self.stopped = True

    self.parse_registers(new_registers)

  def step_single(self):
    if not self.stopped:
      self.stopped = True
      print("Machine was running, stopping")

    new_registers = self.network.step_single();
    self.parse_registers(new_registers)

  def step_line(self):
    if not self.stopped:
      self.stopped = True
      print("Machine was running, stopping")

    new_registers = self.network.step_line();
    self.parse_registers(new_registers)

  def breakpoint_cip_add(self, cip):
    new_registers = self.network.breakpoint_cip_add(cip);
    self.parse_registers(new_registers)    

  def breakpoint_cip_remove(self, cip):
    new_registers = self.network.breakpoint_cip_remove(cip);
    self.parse_registers(new_registers)