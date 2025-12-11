from abc import ABC, abstractmethod
from typing import Annotated
from random import randint

from components.mm_component import MemoryMappedComponent

SECTORED_STORAGE = 0b00010000
IS_BOOTABLE      = 0b00000100

class BlockDevice(ABC):
    @abstractmethod
    def fetch(self, sector: int, addr: int) -> int: return 0x00
    @abstractmethod
    def write(self, sector: int, addr: int, val: int) -> None: pass
    @abstractmethod
    def status(self) -> int: pass

class HardDiskDrive(BlockDevice):
    def __init__(self, data: Annotated[bytearray, 65536], bootable: bool):
        self.data = data
        self.bootable = bootable
        
    def fetch(self, sector: int, addr: int) -> int:
        try:
            return self.data[sector * 256 + addr]
        except IndexError:
            return randint(0x00, 0xff)
    
    def write(self, sector: int, addr: int, val: int) -> None:
        try:
            self.data[sector * 256 + addr] = val
        except IndexError:
            pass
        
    def status(self) -> int:
        status = SECTORED_STORAGE
        
        if self.bootable: status |= IS_BOOTABLE
        
        return status
    
class BootableDrive(HardDiskDrive):
    def __init__(self, path: str):
        with open(path, "rb") as f:
            super().__init__(f.read(), bootable=True)
        
class NonBootableDrive(HardDiskDrive):
    def __init__(self, path: str):
        with open(path, "rb") as f:
            super().__init__(f.read(), bootable=False)

class BlockDeviceInterface(MemoryMappedComponent):
    def __init__(self, sector: int, status: int, selector: int, readout: int) -> None:
        self.sector_addr = sector
        self.selector_addr = selector
        self.status_addr = status
        
        self.sector = randint(0x00, 0xff)
        self.selected = randint(0x00, 0xff)
        
        self.readout_start = readout
        self.devices: list[BlockDevice|None] = [None] * 256
        
    def device_fetch(self, addr: int) -> int:
        byte = addr - self.readout_start
        return self.devices[self.selected].fetch(self.sector, byte)
    def device_write(self, addr: int, val: int) -> int:
        byte = addr - self.readout_start
        return self.devices[self.selected].write(self.sector, byte, val)
        
    def contains(self, addr: int) -> bool:
        return addr in [self.sector_addr, self.status_addr, self.selector_addr] or \
            (self.readout_start <= addr <= self.readout_start + 0xff)
    
    def fetch(self, addr: int) -> int:
        if addr == self.sector_addr:
            return self.sector
        
        if addr == self.selector_addr:
            return self.selected
        
        if addr == self.status_addr:
            if self.devices[self.selected] is None: return 0b00000000
            return self.devices[self.selected].status()
        
        if self.devices[self.selected] is None:
            return randint(0x00, 0x0ff) # simulating floating pins or something
                                        # along those lines
        
        return self.device_fetch(addr)
    
    def write(self, addr: int, val: int) -> None:
        if addr == self.status_addr:
            return
        
        if addr == self.selector_addr:
            self.selected = val
            return
        
        if addr == self.sector_addr:
            self.sector = val
            return
        
        self.device_write(addr, val)