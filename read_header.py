#!/usr/bin/python

import re, hashlib, os, io, argparse, sys, zlib
from configparser import ConfigParser
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter

cmdparser = argparse.ArgumentParser(
    description="Read and extract data from SuperMicro IPMI firmware"
)
cmdparser.add_argument(
    "--extract", action="store_true", help="Extract any detected firmware images"
)
cmdparser.add_argument("filename", help="Filename to read from")
args = cmdparser.parse_args()

default_ini = """
[flash]
total_size=0

[global]
major_version=0
minor_version=0
footer_version=2
type=unknown

[images]
"""

bootloader_md5sums = {
    "649f3b6a0c9d67ff90c6d9daaa4dd9b9": "WPCM450 Boot Loader [ Version:1.0.14 ] Rebuilt on Oct 15 2010",
    "166162c6c9f21d7a710dfd62a3452684": "WPCM450 Boot Loader [ Version:1.0.14 ] Rebuilt on Mar 23 2012",
}

config = ConfigParser()
config.read_string(default_ini)

with open(args.filename, "rb") as f:
    ipmifw = f.read()

config.set("flash", "total_size", str(len(ipmifw)))

try:
    os.mkdir("data")
except OSError:
    pass

print("Read %i bytes" % len(ipmifw))

fwtype = "unknown"
if len(ipmifw) > 0x01FC0000:
    if ipmifw[0x01FC0000:0x01FC0005] == b"[img]":
        fwtype = "aspeed"

if fwtype == "unknown":
    bootloader = ipmifw[:64040]
    bootloader_md5 = hashlib.md5(bootloader).hexdigest()
    if bootloader_md5 not in bootloader_md5sums.keys():
        print(
            "Warning: bootloader (first 64040 bytes of file) md5 doesn't match.  This parser may not work with a different bootloader"
        )
        print(
            "Expected %s, got %s"
            % (" or ".join([x for x in bootloader_md5sums.keys()]), bootloader_md5)
        )
    else:
        print("Detected valid bootloader: %s" % bootloader_md5sums[bootloader_md5])
        fwtype = "winbond"

print()
config.set("global", "type", fwtype)

if fwtype == "winbond":
    from ipmifw.Winbond import Winbond

    firmware = Winbond()
    firmware.parse(ipmifw, args.extract, config)

elif fwtype == "aspeed":
    from ipmifw.ASpeed import ASpeed

    config.set("global", "footer_version", "3")
    firmware = ASpeed()
    firmware.parse(ipmifw, args.extract, config)

else:
    print("Error: Unable to determine what type of IPMI firmware this is!")
    sys.exit(1)


if args.extract:
    with open("data/image.ini", "w") as f:
        config.write(f)
else:
    print("\nConfiguration info:\n")
    config.write(sys.stdout)
