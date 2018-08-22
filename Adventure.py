import cmd

from Network import DebuggerOfflineException

class Adventure(cmd.Cmd):
  intro = """You woke up in a strange place. People around you
are wearing either green or purple outfits, and are
carrying guns. What do you do?"""
  prompt = '>>> '

  def __init__(self, printer, debugger):
    super().__init__()

    self.printer = printer
    self.debugger = debugger

  def do_break(self, line):
    'Stop right there!'
    try:
      print("You threw a wrench in the works")
      self.debugger.stop()
    except DebuggerOfflineException:
      print("Debugger is offline, could not stop")

  do_stop = do_break

  def do_step(self, line):
    'Little step for a man...'
    try:
      print("You tip-toed forward a bit")
      self.debugger.step_single()
    except DebuggerOfflineException:
      print("Debugger is offline, could not step")

  def do_line(self, line):
    '...giant leap for mankind'
    try:
      print("You leaped forward")
      self.debugger.step_line()
    except DebuggerOfflineException:
      print("Debugger is offline, could not step")

  def do_breakpoint(self, line):
    """When you see this guy, drop whatever you are doing. Or forget about it
    `[b]reakpoint [a]dd 80`
    `[b]reakpoint [r]emove 80`
    """
    mode, cip = (line.split(' ') + [None])[:2]

    cip = int(cip, 0)

    try:
      if mode in ['add', 'a']:
        print("Stop when you see {}".format(cip))
        self.debugger.breakpoint_cip_add(cip)
      elif mode in ['remove', 'r']:
        print("Cancel stopping when you see {}".format(cip))
        self.debugger.breakpoint_cip_remove(cip)
    except DebuggerOfflineException:
      print("Debugger is offline, could not execute this action")

  do_b = do_breakpoint

  def do_memory(self, line):
    """Mind-reading. Get the current AMX read into memory state.
    [m]emory offset length
    """

    offset, length = (line.split(' ') + [None])[:2]
    if not offset.isnumeric():
      print("Offset is required")
      return

    offset = int(offset, 0)

    if length is None:
      length = 10
    else:
      length = int(length, 0)

    try:
      self.debugger.query_memory(offset, length)
    except DebuggerOfflineException:
      print("Debugger is offline, could not update")
      return

    self.printer.print_memory(offset, length)

  do_m = do_memory

  def do_register(self, line):
    """Shows current value of specified register. Add "force" to query for ALL registers if machine is currently running"""

    register, force = (line.split(' ') + [None])[:2]
    force = force == 'force'
    if force:
      try:
        self.debugger.query_registers()
      except DebuggerOfflineException:
        print("Debugger is offline, could not update")
        return

    register = register.upper()

    keys = self.debugger.registers.keys()
    if not register in keys:
      print(f'Invalid register specified. Available keys: {", ".join(keys)}')
      return

    self.printer.print_register(register, force)

  do_reg = do_register

  def do_registers(self, line):
    'Shows current value of all registers. If you see dead cows, run! Add "force" to query for current values if machine is currently running'

    force = line == 'force'
    if force:
      if self.debugger.stopped:
        print("This really was not necessary")

      try:
        self.debugger.query_registers()
      except DebuggerOfflineException:
        print("Debugger is offline, could not update")
        return

    self.printer.print_registers(force)

  do_regs = do_registers

  def do_run(self, line):
    'Run until you decide not to anymore (or decided beforehand)'

    try:
      if self.debugger.run():
        print('Yup, now it is running')
      else:
        print('It was running, or could not start for some reason')
    except DebuggerOfflineException:
      print("Debugger is offline, could not update")

  def do_hello(self, line):
    'Say hi'
    print("Well, hello to you too")

  def do_bye(self, line):
    'Exit the adventure'
    return True

  do_exit = do_quit = do_bye

  def default(self, line):
    print("I don't know what you mean. Type \"?\" or \"help\" to list available commands")

  def do_shell(self, line):
    print("I won't obey if you keep using this tone!")

  def precmd(self, line):
    if len(line) and line == line.upper():
      print("Please don't shout")

    line = line.lower()

    return line