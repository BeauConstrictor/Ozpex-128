from typing import Annotated
from random import randint

from components.mm_component import MemoryMappedComponent

class DiskSlot(MemoryMappedComponent):
    def __init__(self, sector: int, status: int, selector: int, readout: int) -> None:
        self.sector_addr = sector
        self.selector_addr = selector
        self.status_addr = status
        
        self.sector = randint(0x00, 0xff)
        self.disk = randint(0x00, 0xff)
        
        self.readout_start = readout
        self.disks = [None] * 256
        
    def contains(self, addr: int) -> bool:
        return addr in [self.sector_addr, self.status_addr, self.selector_addr] or \
            (self.readout_start <= addr <= self.readout_start + 0xff)
    
    def fetch(self, addr: int) -> int:
        if addr == self.sector_addr:
            return self.sector
        
        if addr == self.selector_addr:
            return self.disk
        
        if addr == self.status_addr:
            status = 0b00000000
            if self.disks[self.disk] is not None: status |= 0b00000001
            return status
        
        if self.disks[self.disk] is None:
            return randint(0x00, 0x0ff) # simulating floating pins or something
                                        # along those lines
        
        byte_in_sector = addr - self.readout_start
        byte = self.sector * 256 + byte_in_sector
        
        try:
            return self.disks[self.disk][byte]
        except IndexError:
            return randint(0x00, 0xff)
    
    def write(self, addr: int, val: int) -> None:
        if addr == self.status_addr:
            return
        
        if addr == self.selector_addr:
            self.disk = val
            return
        
        if addr == self.sector_addr:
            self.sector = val
            return
        
        # TODO: make changes persistent
        if self.readout_start <= addr <= self.readout_start + 0xff and self.disks[self.disk] is not None:
            byte_in_sector = addr - self.readout_start
            byte = self.sector * 256 + byte_in_sector
            self.disks[self.disk][byte] = val & 0xFF