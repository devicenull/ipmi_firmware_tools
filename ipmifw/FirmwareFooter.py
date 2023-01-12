#!/usr/bin/python

import struct, zlib

class FirmwareFooter:
    # Footer version 1:
    # ATENs_FW MAJOR MINOR CHECKSUM

    # Footer version 2:
    # ATENs_FW MAJORVER MINORVER 0x71 CHECKSUM 0x17

    # Footer version 3:
    # ATENs_FW MAJORVER MINORVER ROOTFS_NFO 0x71 WEBFS_NFO 0x17

    def __init__(self):
        # these together get you the firmware version: rev1.rev2
        self.rev1 = 0
        self.rev2 = 0
        self.checksum = 0
        self.rootfs_nfo = 0
        self.webfs_nfo = 0
        # fwtag appears to be some way of recogizing that this is indeed a footer
        # should be 0x71
        self.fwtag1 = 0x71
        # should be 0x17
        self.fwtag2 = 0x17
        self.footerver = 3

    def loadFromString(self, footer):
        if len(footer) >= 20:
            (self.rev1, self.rev2, self.rootfs_nfo, self.fwtag1, self.webfs_nfo, self.fwtag2) = struct.unpack(b"<BB8sB8sB", footer)
        # Older footer versions have tags at different offset
        if len(footer) < 20 or self.fwtag1 != 0x71 or self.fwtag2 != 0x17:
            self.footerver = 2
            (self.rev1, self.rev2, self.fwtag1, self.checksum, self.fwtag2) = struct.unpack(b"<BBBIB", footer)
            # Seems firmware older then v3.00 uses a different footer, which doesn't have the tag
            if self.fwtag1 != 0x71 or self.fwtag2 != 0x17:
                (self.rev1, self.rev2, self.checksum) = struct.unpack(b"<BBI", footer[:6])
                self.footerver = 1
                self.fwtag1 = 0
                self.fwtag2 = 0

    def getRawString(self):
        if self.footerver == 3:
            contents = b'ATENs_FW'+struct.pack(b"<BB8sB8sB", self.rev1, self.rev2, self.rootfs_nfo.encode('ISO-8859-1'), self.fwtag1, self.webfs_nfo.encode('ISO-8859-1'), self.fwtag2)
        elif self.footerver == 2:
            contents = b'ATENs_FW'+struct.pack(b"<BBBIB", self.rev1, self.rev2, self.fwtag1, self.checksum, self.fwtag2)
        else:
            contents = b'ATENs_FW'+struct.pack(b"<BBI", self.rev1, self.rev2, self.checksum)
        return contents

    def __str__(self):
        return "Firmware footer version %i firmware version %i.%i checksum: 0x%x tag: 0x%x%x rootfs_nfo: 0x%s webfs_nfo: 0x%s" % (self.footerver, self.rev1, self.rev2, self.checksum, self.fwtag1, self.fwtag2, self.rootfs_nfo, self.webfs_nfo)

    def computeFooterChecksum(self, imagecrc):
        rawCRCBuf = b''
        for cur in imagecrc:
            rawCRCBuf += struct.pack(b"<I",cur)

        return (zlib.crc32(rawCRCBuf) & 0xffffffff)

