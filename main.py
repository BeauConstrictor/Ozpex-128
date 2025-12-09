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
from components.disk import DiskSlot
from components.mm_component import MemoryMappedComponent

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ozpex-128",
        description = "A fictional 8-bit computer and emulator based on the "
                      "6502",
    )
                         
    parser.add_argument("-b", "--bios",
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "bin", "bios"),
                        help="overwrite the default bios rom")
    
    for i in range(256):
        parser.add_argument(
            f'--disk{i}',
            f'-{i}',
            type=str,
            default=None,
            help=argparse.SUPPRESS,
        )
        
    parser.add_argument("-X", "--diskX",
                        action="store_true",
                        help="load a disk image into disk slot X")

    
    parser.add_argument("--debug",
                        action="store_true",
                        help="watch the emulator execute individual instructions")
    
    parser.add_argument("-n", "--nocrash",
                        action="store_true",
                        help="disable crashes on unknown opcodes")
    
    parser.add_argument("-g", "--gui",
                        action="store_true",
                        help="start the ozpex 64 gui (ignores other arguments)")
    
    return parser.parse_args()

def create_machine(args: argparse.Namespace) -> Cpu:

    # MEMORY MAP:
    # $0000 - $BFFF: RAM
    #  > $0000 - $00ff: ZERO PAGE
    #  > $0100 - $01ff: HARDWARE STACK
    #  > $0200 - $02ff: BOOTLOADER
    # $C000 - $C1FF: I/O BLOCK
    #  > $C000:         SERIAL PORT
    #  > $C001:         TIMER REG A
    #  > $C002:         TIMER REG B
    #  > $C003:         DISK SECTOR
    #  > $C004:         DISK SELECT
    #  > $C005:         DISK STATUS
    #  > $C006 - $C0FF: FUTURE USE
    #  > $C100 - $C1FF: DISK SECTOR DATA
    # $C200 - DFFF: UNMAPPED
    # $E000 - FFFF: BIOS ROM
    
    cpu = Cpu({
        "ram": Ram(0x0000, 0xbfff),
        "serial": SerialPort(0xc000),
        "timer": Timer(0xc001, 0xc002),
        "diskslot": DiskSlot(sector=0xc003, status=0xc005, selector=0xc004, readout=0xc100),
        "rom": Rom(0xe000, 0xffff),
    })

    with open(args.bios, "rb") as f:
        bios_data = list(f.read())
    cpu.mm_components["rom"].load(bios_data, cpu.mm_components["rom"].start)
    
    for i in range(256):
        disk_path = getattr(args, f'disk{i}')
        if disk_path is not None:
            with open(disk_path, "rb") as f:
                disk_data = list(f.read())
            cpu.mm_components["diskslot"].disks[i] = disk_data
    
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
            print("\n\n\033[31m", end="", file=stderr)
            print(f"emu: {e}, execution aborted.", end="", file=stderr)
            print("\033[0m", file=stderr)
            exit(1)
        if debug:
            cpu.visualise(instr)
            input()

def main() -> None:
    args = parse_args()
    
    if not os.path.exists(args.bios):
        print("\033[31memu: cannot find the bios rom.\033[0m", file=stderr)
        exit(1)
    
    if args.gui:
        import gui.main
        gui.main.App().mainloop()
        return
    
    cpu = create_machine(args)
    
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
        print("\n\n\033[31m", end="", file=stderr)
        print(f"emu: ctrl+c exit.", end="", file=stderr)
        print("\033[0m", file=stderr)
        exit(0)
