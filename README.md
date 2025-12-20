# Ozpex 128

The Ozpex 128 is a fictional, extensible 8-bit computer architecture designed as the successor to the [Ozpex 64](https://github.com/BeauConstrictor/Ozpex-64) based on the 6502 CPU.

![GNU AGPL v3.0 License](https://img.shields.io/github/license/BeauConstrictor/ozpex-128?style=flat)

The Ozpex 128 expands the design of the 64 to be more modular, more powerful, and better suited for running a general-purpose operating system.

This repository contains:

- The full architecture spec.

- An emulator that can be easily integrated into other programs.

- A minimal BIOS

## Extensibility

The core of the 128's philosophy is extensibility, so you can tailor a specific configuration to your needs, and software will accept that system gracefully.

Every Ozpex 128 configuration includes a basic set of resources at predefined memory addresses, which altogether form the *standard environment*. The standard environment is guaranteed to be present on any Ozpex 128 computer, so a running program can rely on it, and query for extra hardware extensions at runtime. This environment features 48KiB of RAM, a serial port for I/O and a hardware timer. For more details on this system, see [the architecture](#the-architecture).

## Using the Emulator

The emulator included in this repository lets you run Ozpex 128 programs, interact with serial I/O, and test storage devices.

### 1. Install & Build

```sh
$ git clone "https://github.com/beauconstrictor/ozpex-128"
$ cd ozpex-128
$ make
```

This will download the emulator from the repo hosted on GitHub and build the BIOS, which is automatically loaded by the emulator.

### 2. Running the Emulator

To start the emulator with a bootable disk image:

```sh
python3 main -0 hdd:bin/testos
```

This command will start the emulator with one extension to the standard environment, a bootable disk drive in device slot 0. `bin/testos` is an operating system that repeatedly prints the text 'Hello, World' every 256ms, a good test of the BIOS, disk drive, serial I/O and hardware timer.

Breaking down the argument:

- `-0 hdd:bin/testos` is what installs this drive.
- `-0` specifies which slot (between 0-255) to place the device in. `hdd` specifies that the device we want to add is a hard disk drive (see [Device Types](#device-types)).
- `:bin/testos` tells the disk drive to load the disk image at the path `./bin/testos`.

Block devices (e.g., disks, extended RAM) can be passed to the emulator as command-line options or configuration fields depending on how your emulator is structured.

### Device Types

`hdd` is not the only device that can be installed. This is a list of all the devices supported by the emulator:

- `hdd:<image>` - A hard disk drive (changes are not replicated to the image file)
- `xmem` - a 64KiB RAM expansion

More devices will be implemented in the future.

## The BIOS

This repository also includes a simple BIOS that simply boots to the first device marked as bootable. Since this BIOS only relies on features present in the standard environment, it should be transferable as a base BIOS to run on any implementation of the architecture.

During boot, the BIOS will pause for 2 seconds, and if the user presses `ESC` during this time, the startup will be cancelled and a small boot menu will appear, showing a list of installed devices and their statuses. From this menu, you can manually select a device to boot to, which might be useful when installing an OS or booting from an external device. If `ESC` is not pressed, the boot continues as normal.

## The Architecture

For more thorough details (pull requests improving the clarity of this document are welcome), see the [architecture.md](https://github.com/BeauConstrictor/Ozpex-128/blob/main/architecture.md), which documents everything you should know to develop for the 128, or to implement the architecture yourself.

## Contributing

Contributions are welcome! New ideas or concepts are especially welcome, as well as bug reports and patches.

## License

This project is licensed under the [GNU AGPL-3.0](https://github.com/BeauConstrictor/Ozpex-128/blob/main/LICENSE).
