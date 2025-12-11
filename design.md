# Ozpex 128

The Ozpex 128 is designed to be a successor to the [Ozpex 64](https://github.com/BeauConstrictor/Ozpex-64). The 128 features a more extensible architecture and is suited to running a general-purpose operating system than the 64 was. This computer uses the same 6502 CPU that was found in the 

This repository contains the architecture of the computer, as well as an accompanying emulator.

## Memory Map

Most of the 6502's 64K of memory is consumed by the 48K of standard RAM at the bottom of the address space. At the top is an 8K BIOS ROM (notably, this is smaller than the 16K ROM of the Ozpex 64).

### Devices

Sandwiched between these at `$C000` to `C1FF` (inclusive) is the device space. 

#### Serial Devices

The lower 256 bytes of this space contain the serial devices, which are mapped to physical serial ports which single bytes can be read from and written to. These devices have no standard way of identifying themselves so they should only be used at a user's discression. For instance, after selecting to print a file, the user could be presented with a prompt asking which serial port to send the data to, and the program would send the raw ASCII bytes of the file over the chosen port.

Serial device `00` (address `$C000`) is the standard I/O port and is typically connected to a serial terminal.

The next two serial devices are combined to form a hardware timer and work in the same way as the 64's timer.

Serial devices `06-FF` (inclusive) represent miscellaneous serial ports, and a motherboard may or may not map these addresses to any number of physical ports.

#### Block Devices

Serial devices `03-05` (inclusive) are dedicated to the managing the block devices. Block devices can serve a wider variety of functions than the serial devices, as there is a standard way for block devices to identify themselves, so a program that requires a certain device can find it and throw an error if it does not exist.

Serial device `03` selects the currently active sector of the current block device. Block devices can have 256 different sectors of 256 bytes in size (this means block devices can store 64K without additional banking techniques). To read or write to the data in a sector, use addresses `$C100-$C1FF`.

Serial device `04` selects the active block device. Since this value is one byte in size, a 128 motherboard can support at most 256 different block devices. These devices would likely take the form of expansion cards & slots in a motherboard.

Serial device `05` cannot be written to, and contains the 'status' of the current block device. This is the format of the status byte:

```text
0    0    0    0 |   0    0    0    0
device identifier|device status flags
```

The device identifier is a value from 0-15 that says which of the standard APIs the device supports. If the value is 0, there is no device occupying the slot. If it is 15, the device does not support any standard api, and sector `FF` will contain a null-terminated string representing whatever freeform identifier the manufacturer chooses for the device. Devices of this type will require special support from drivers or a similar machanism in the operating system.

The least significant (rightmost) flag bit represents whether the device should be ignored. The motherboard will enablgue this bit if the device has failed so that software can report the device as present but malfunctioning to the end user. The second bit from the right is the busy flag. is this bit is set, the device is occupied with some job and software should wait before interacting with the device (an interaction counts as any block device-related action with this device set as active, excluding switching to another device or reading the device status). The third bit from the right tells the BIOS whether the device is bootable, so should usually be ignored. Generally, physical switches next to the expansion slots in a motherboard will control this bit. The most significant flag bit is reserved for future use.

##### Standard APIs

There are a few standard APIs for common block devices with similar functionality to minimise the need for complex drivers.

###### Sectored Storage

Sectored storage should be reported with a device identifier of 1. Sectored storage can be a HDD, floppy drive, SSD and so on. The 64K represents the full contents of the disk, split into arbitrary sectors (not necessarily representative of the physical medium's sectoring). When the sector byte is written to, the 256 bytes at that sector will be buffered in a small memory chip which can be freely read to and written to in the block device area of memory. When the sector is changed again, the contents of this chip will be copied over into the permanent storage medium. The only time the busy flag will be true is after a sector change, so you should check that the flag is false before changing sector again or reading or writing to the new sector, as the results are undefined when the device is busy. To quickly flush changes to the physical medium, one can do this:

```
  sta $c003     ; flush the sector changes
busy_wait:
  lda $c005     ; read the device status
  and %00000010 ; check the busy flag
  bne busy_wait ; keep checking if the device is busy
```

It doesn't matter if this `sta` results in a new sector value. In fact, a `lda $c003` immediately beforehand will not cause problems, as it is simply the act of writing to the sector byte that causes the flush, not actually changing the active sector.

###### Extended Memory

While 48K is generous for a 6502-based system, some programs will need more than this (the 'standard environment'). If a memory allocator run out of space in standard memory, it does not need to immediately throw an error, as it may first loop over all the block devices to find any extended memory (device identifier 2). Extended memory is easy and fast to use as the busy flag will never be true, so no waiting is needed. In addition, you do not need to flush the sector, as it is a direct window into the RAM chip and not a buffer. Each extended memory device installed will add 64K of available RAM to the machine, so it is possible to very quickly increase the amount of RAM available to your machine. The downside of exended memory is that you only get a 256 byte window at a time, so you must frequently switch sectors when accessing distant areas of an extended memory device's address space.

## Boot Process

When the computer boots, the CPU reads address `$FFFC-$FFFD` (contained in the BIOS ROM) and jumps to the address stored there. Usually, this will be address `$E000`, the start of the BIOS ROM. The BIOS will scan all block devices from 0 to 255 and pick the first device it finds that it marked as bootable. Once it has found a bootable device, it will load sector 0 of that device into address `$200` and jump there.

This program in this sector is known as the bootloader and is free to do whatever it needs, as it has full control of the computer. Usually, the BIOS will do one of 3 things:

1. Load some more sectors off disk containing the rest of the OS (if it is not stored in a filesystem)
2. Load some more sectors containing the rest of the bootloader, which will do either option 1 or 2 (some filesystems are too complex to parse in a 256 byte program, for example)
3. Parse the filesystem and load & run some kernel file.

Since the BIOS ROM is 8K, there is a lot of space for a more complex system, as a simple BIOS can be less than 200 bytes. A motherboard vendor can ship a BIOS that allows you to select which devices are marked as bootable from within software, or change the clock speed, etc.. Undefined regions of memory allow the BIOS to interface directly with the motherboard without interfering with the standard environment that programs expect.
