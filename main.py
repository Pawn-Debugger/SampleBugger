import sys
import socket
import threading

import Adventure
import Debugger
import Network
import Printer

if __name__ == '__main__':
  network = Network.Network()
  debugger = Debugger.Debugger(network)
  printer = Printer.Printer(debugger)

  adventure = Adventure.Adventure(printer, debugger).cmdloop()