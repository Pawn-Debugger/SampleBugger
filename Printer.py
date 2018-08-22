class Printer:
  def __init__(self, debugger):
    self.debugger = debugger

  def volatile_warning(self):
    print("(Will change in a microsecond, don't get too attached)")

  def dump_register(self, register):
    print('{register}: 0x{hexvalue:06X}'.format(register=register, hexvalue=self.debugger.registers[register]))

  def print_registers(self, forced):
    if forced:
      self.volatile_warning()
    elif not self.debugger.stopped:
      print("(Those are last known values)")

    for register in self.debugger.registers.keys():
      self.dump_register(register)

  def print_register(self, register, forced):
    if forced:
      self.volatile_warning()

    self.dump_register(register)

  def print_memory(self, offset, length):
    print(self.debugger.memory[offset:offset + length])
