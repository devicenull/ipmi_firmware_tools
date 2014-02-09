import struct, zlib

class FirmwareFooter:
	# Footer version 1:
	# ATENs_FW MAJOR MINOR CHECKSUM

	# Footer version 2:
	# ATENs_FW MAJORVER MINORVER 0x71 CHECKSUM 0x17

	def __init__(self):
		# these together get you the firmware version: rev1.rev2
		self.rev1 = 0
		self.rev2 = 0
		self.checksum = 0
		# fwtag appears to be some way of recogizing that this is indeed a footer
		# should be 0x71
		self.fwtag1 = 0x71
		# should be 0x17
		self.fwtag2 = 0x17
		self.footerver = 2

	def loadFromString(self, footer):
		(self.rev1, self.rev2, self.fwtag1, self.checksum, self.fwtag2) = struct.unpack("<bbbIb", footer)
		# Seems firmware older then v3.00 uses a different footer, which doesn't have the tag
		if self.fwtag1 != 0x71 or self.fwtag2 != 0x17:
			(self.rev1, self.rev2, self.checksum) = struct.unpack("<bbI", footer[:6])
			self.footerver = 1
			self.fwtag1 = 0
			self.fwtag2 = 0

	def getRawString(self):
		if self.footerver == 2:
			contents = "ATENs_FW"+struct.pack("<bbbIb", self.rev1, self.rev2, self.fwtag1, self.checksum, self.fwtag2)
		else:
			contents = "ATENs_FW"+struct.pack("<bbI", self.rev1, self.rev2, self.checksum)
		return contents

	def __str__(self):
		return "Firmware footer version %i firmware version %i.%i checksum: 0x%x tag: 0x%x%x" % (self.footerver, self.rev1, self.rev2, self.checksum, self.fwtag1, self.fwtag2)

	def computeFooterChecksum(self, imagecrc):
		rawCRCBuf = ""
		for cur in imagecrc:
			rawCRCBuf += struct.pack("<I",cur)

		return (zlib.crc32(rawCRCBuf) & 0xffffffff)

