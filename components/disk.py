from typing import Annotated
from random import randint

from components.mm_component import MemoryMappedComponent

class Disk(MemoryMappedComponent):
    def __init__(self, sector: int, status: int, readout: int,
                 data: Annotated[bytearray, 65536]|None) -> None:
        self.sector_addr = sector
        self.status_addr = status
        
        self.sector = randint(0x00, 0xff) # unintialised
        
        self.readout_start = readout
        self.data = data
        
    def contains(self, addr: int) -> bool:
        return addr in [self.sector_addr, self.status_addr] or \
            (self.readout_start <= addr <= self.readout_start + 0xff)
    
    def fetch(self, addr: int) -> int:
        if addr == self.sector_addr:
            return self.sector
        
        if addr == self.status_addr:
            status = 0b00000000
            if self.data is not None: status |= 0b00000001
            return status
        
        if self.data is None:
            return randint(0x00, 0x0ff) # simulating floating pins or something
                                        # along those lines
        
        byte_in_sector = addr - self.readout_start
        byte = self.sector * 256 + byte_in_sector
        return self.data[byte]
    
    def write(self, addr: int, val: int) -> None:
        if addr == self.status_addr:
            return
        if addr == self.sector_addr:
            self.sector = val
            return
        
        # TODO: make changes persistent
        if self.readout_start <= addr <= self.readout_start + 0xff and self.data:
            byte_in_sector = addr - self.readout_start
            byte = self.sector * 256 + byte_in_sector
            self.data[byte] = val & 0xFF