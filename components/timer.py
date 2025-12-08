from components.mm_component import MemoryMappedComponent

import time

def break_word(word: int) -> tuple[int, int]:
    low = word & 0xff
    high = (word >> 8) & 0xff
    return high, low

class Timer(MemoryMappedComponent):
    """
    The Timer is designed for precisely measuring time elapsed.
    The Timer contains two registers: a & b.
    
    Since time is read as a 16-bit value in ms, times above 65s cannot be read
    by default. Time elapsed is effectively divided by b to result in the final
    reading, so longer times can be measured by reducing accuracy.
    
    The Timer should always be intialised by writing to a before first read.
    
    a:
        - write anything here to start the timer.
        - read time elapsed since the last write to a (low byte).
        
    b:
        - write to set milliseconds per 1 unit in time readout
        - read time elapsed since the last write to a (high byte)
    """
    
    def __init__(self, reg_a: int, reg_b: int) -> None:
        self.reg_a = reg_a
        self.reg_b = reg_b
        
        self.begin = 0
        self.resolution = 1 # ms per tick
        
    def contains(self, addr: int) -> bool:
        return addr in [self.reg_a, self.reg_b]
    
    def fetch(self, addr: int) -> int:
        elapsed = (time.monotonic() - self.begin) * 1000 // self.resolution
        elapsed = int(elapsed) & 0xffff
        
        if addr == self.reg_a:
            return break_word(elapsed)[1]
        elif addr == self.reg_b:
            return break_word(elapsed)[0]
    
    def write(self, addr: int, val: int) -> None:
        if addr == self.reg_a:
            self.begin = time.monotonic()
        elif addr == self.reg_b:
            self.resolution = max(1, val) # prevent div by 0