#!/usr/local/bin/python2.7

import re, hashlib, os, io, argparse, sys, zlib
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter


class Winbond:
	def __init__(self, ipmifw):
		self.ipmifw = ipmifw

	def parse(self, extract, config):
		bootloader = self.ipmifw[:64040]
		bootloader_md5 = hashlib.md5(bootloader).hexdigest()


		if extract:
			print "Dumping bootloader to data/bootloader.bin"
			with open('data/bootloader.bin','w') as f:
				f.write(bootloader)


		imagecrc = []
		# Start by parsing all the different images within the firmware
		# This method comes directly from the SDK.  Read through the file in 64 byte chunks, and look for the signature at a certain point in the string
		# Seems kinda scary, as there might be other parts of the file that include this.
		for i in range(0,len(self.ipmifw),64):
			footer = self.ipmifw[i:i+64]

			fi = FirmwareImage()
			# 12 bytes of padding.  I think this can really be anything, though it's usually \xFF
			fi.loadFromString(footer[12:])

			if not fi.isValid():
				continue

			print "\n"+str(fi)

			imagestart = fi.base_address
			if imagestart > 0x40000000:
				# I'm unsure where this 0x40000000 byte offset is coming from.  Perhaps I'm not parsing the footer correctly?
				imagestart -= 0x40000000

			imageend = imagestart + fi.length

			curcrc = zlib.crc32(self.ipmifw[imagestart:imageend]) & 0xffffffff
			imagecrc.append(curcrc)

			if extract:
				print "Dumping 0x%s to 0x%s to data/%s.bin" % (imagestart, imageend, fi.name)
				with open('data/%s.bin' % fi.name.replace("\x00",""),'w') as f:
					f.write(self.ipmifw[imagestart:imageend])
				computed_image_checksum = FirmwareImage.computeChecksum(self.ipmifw[imagestart:imageend])

				if computed_image_checksum != fi.image_checksum:
					print "Warning: Image checksum mismatch, footer: 0x%x computed: 0x%x" % (fi.image_checksum,computed_image_checksum)
				else:
					print "Image checksum matches"


			config.set('images', str(fi.imagenum), 'present')
			configkey = 'image_%i' % fi.imagenum
			config.add_section(configkey)
			config.set(configkey, 'length', hex(fi.length))
			config.set(configkey, 'base_addr', hex(fi.base_address))
			config.set(configkey, 'load_addr', hex(fi.load_address))
			config.set(configkey, 'exec_addr', hex(fi.exec_address))
			config.set(configkey, 'name', fi.name)
			config.set(configkey, 'type', hex(fi.type))

		# Next, find and validate the global footer
		for imageFooter in re.findall("ATENs_FW(.{8})",self.ipmifw,re.DOTALL):
			footer = FirmwareFooter()
			footer.loadFromString(imageFooter)
			computed_checksum = footer.computeFooterChecksum(imagecrc)

			print "\n"+str(footer)

			if footer.checksum == computed_checksum:
				print "Firmware checksum matches"
			else:
				print "Firwamre checksum mismatch, footer: 0x%x computed: 0x%x" % (footer.checksum, computed_checksum)

			config.set('global', 'major_version', footer.rev1)
			config.set('global', 'minor_version', footer.rev2)
			config.set('global', 'footer_version', footer.footerver)

