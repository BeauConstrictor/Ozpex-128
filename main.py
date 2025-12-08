import os.path
import argparse
from sys import stderr
from time import sleep
from typing import Iterator

from components.cpu import Cpu
from components.ram import Ram
from components.rom import Rom
from components.timer import Timer
from components.serial import SerialPort
from components.disk import Disk
from components.mm_component import MemoryMappedComponent

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ozpex-128",
        description = "A fictional 8-bit computer and emulator based on the "
                      "6502",
    )
                         
    parser.add_argument("-b", "--bios",
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "roms", "monitor.bin"),
                        help="overwrite the default bios rom")
    
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="watch the emulator execute individual instructions")
    
    parser.add_argument("-n", "--nocrash",
                        action="store_true",
                        help="disable crashes on unknown opcodes")
    
    parser.add_argument("-g", "--gui",
                        action="store_true",
                        help="start the ozpex 64 gui (ignores other arguments)")
    
    return parser.parse_args()

def create_machine(rom: str) -> Cpu:

    # MEMORY MAP:
    # $0000 - $BFFF: RAM
    # $C000 - $C1FF: I/O BLOCK
    #  > $C000:         SERIAL PORT
    #  > $C001:         TIMER REG A
    #  > $C002:         TIMER REG B
    #  > $C003:         DISK SECTOR SELECTOR
    #  > $C005:         DISK STATUS
    #  > $C006 - $C0FF: FUTURE USE
    #  > $C100 - $C1FF: DISK SECTOR DATA
    # $C200 - DFFF: UNMAPPED
    # $E000 - FFFF: BOOTLOADER/BIOS ROM
    
    cpu = Cpu({
        "ram": Ram(0x0000, 0xbfff),
        "serial": SerialPort(0xc0000),
        "timer": Timer(0xc001, 0xc002),
        "disk": Disk(sector=0xc003, status=0xc005, readout=0xc100, data=None),
        "rom": Rom(0xe000, 0xffff),
    })

    with open(rom, "rb") as f:
        rom_data = list(f.read())
    cpu.mm_components["rom"].load(rom_data, 0xc003)
    
    cpu.reset()
    
    return cpu

def simulate(cpu: Cpu, nocrash: bool, debug: bool) -> Iterator[None]:
    cycles_executed = 0
    
    while True:
        try:
            instr = cpu.execute()
            yield
                       
        except NotImplementedError as e:    
            if nocrash: continue
            print("\n\n\033[31m", end="")
            print(f"6502: {e}, execution aborted.", end="")
            print("\033[0m")
            exit(1)
        if debug:
            cpu.visualise(instr)
            input()

def main() -> None:
    args = parse_args()
    
    if args.gui:
        import gui.main
        gui.main.App().mainloop()
        return
    
    cpu = create_machine(args.rom)
    
    cycle = 0
    for _ in simulate(cpu, args.nocrash, args.debug):
        # on my computer, this gets ~1MHz
        if cycle % 200 == 0:
            cycle = 0
            sleep(0.000001)
        cycle += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[31m", end="")
        print(f"emu: ctrl+c exit.", end="")
        print("\033[0m")
        exit(0)
