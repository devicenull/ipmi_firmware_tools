#!/usr/local/bin/python2.7

import re, hashlib, zlib, struct
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter


class ASpeed:
	def __init__(self, ipmifw):
		self.ipmifw = ipmifw

	def parse(self, extract, config):
		footer = self.ipmifw[0x01fc0000:]
		imagenum = 1
		# There's a nice handy block at the end of the file that gives information about all the embedded images!
		for (imagestart, length, checksum, filename) in re.findall("\[img\]: ([0-9a-z]+) ([0-9a-z]+) ([0-9a-z]+) ([0-9a-z\-_.]+)", footer):
			imagestart = int(imagestart,16)
			length = int(length,16)
			checksum = int(checksum,16)

			print "Firmware image: %i Name: %s Base: 0x%x Length: 0x%x CRC32: 0x%x" % (imagenum, filename, imagestart, length, checksum)


			if extract:
				imageend = imagestart + length
				print "Dumping 0x%x to 0x%X to data/%s" % (imagestart, imageend, filename)
				with open('data/%s' % filename,'w') as f:
					f.write(self.ipmifw[imagestart:imageend])

				computed_image_checksum = zlib.crc32(self.ipmifw[imagestart:imageend]) & 0xffffffff
				if computed_image_checksum != checksum:
					print "Warniing: Image checksum mismatch, footer: 0x%x computed 0x%x" % (checksum, computed_image_checksum)
				else:
					print "Image checksum matches"


                        config.set('images', str(imagenum), 'present')
                        configkey = 'image_%i' % imagenum
                        config.add_section(configkey)
                        config.set(configkey, 'name', filename)
                        config.set(configkey, 'base_addr', hex(imagestart))
                        config.set(configkey, 'length', hex(length))
			config.set(configkey, 'checksum', hex(checksum))


			imagenum += 1

		# Next, find and validate the global footer
		for imageFooter in re.findall("ATENs_FW(.{20})",self.ipmifw,re.DOTALL):

			(rev1, rev2, unknown) = struct.unpack("<bb18s", imageFooter)
			print "footer: %x.%x unknown: %s" % (rev1, rev2, unknown)
			#print "\n"+str(footer)

			#if footer.checksum == computed_checksum:
			#	print "Firmware checksum matches"
			#else:
			#	print "Firwamre checksum mismatch, footer: 0x%x computed: 0x%x" % (footer.checksum, computed_checksum)

			config.set('global', 'major_version', rev1)
			config.set('global', 'minor_version', rev2)
			#config.set('global', 'footer_version', footer.footerver)

