import sys

from components.mm_component import MemoryMappedComponent

if sys.platform.startswith("win"):
    import msvcrt

    def getch():
        if msvcrt.kbhit():
            c = msvcrt.getwch()
            if c == '\r': c = '\n'
            return c
        return None

else:
    import select
    import tty
    import termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    def getch():
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None

    import atexit
    
    atexit.register(lambda: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings))

class SerialPort(MemoryMappedComponent):
    def __init__(self, addr: int) -> None:
        self.addr = addr
        
    def contains(self, addr: int) -> bool:
        return addr == self.addr
    
    def fetch(self, addr: int) -> int:
        # the assumption here is that a nul byte will never be typed directly,
        # as they will not be registered by software
        key = getch()
        key = ord(key) if key is not None else 0
        return key & 0xff
    
    def write(self, addr: int, val: int) -> None:
        if val == 0x11: # ascii device control 1:
            sys.stdout.write("\033[2J\033[H")
        else:
            sys.stdout.write(chr(val))
            
        sys.stdout.flush()