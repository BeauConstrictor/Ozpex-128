from abc import ABC, abstractmethod

class MemoryMappedComponent(ABC):
    @abstractmethod
    def contains(self, addr: int) -> bool: ...
    @abstractmethod
    def fetch(self, addr: int) -> int: return 0
    @abstractmethod
    def write(self, addr: int, val: int) -> None: pass