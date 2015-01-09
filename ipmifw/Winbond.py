#!/usr/local/bin/python2.7

import re, hashlib, os, io, argparse, sys, math, zlib
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter


class Winbond:
	def parse(self, ipmifw, extract, config):
		bootloader = ipmifw[:64040]
		bootloader_md5 = hashlib.md5(bootloader).hexdigest()


		if extract:
			print "Dumping bootloader to data/bootloader.bin"
			with open('data/bootloader.bin','wb') as f:
				f.write(bootloader)


		imagecrc = []
		# Start by parsing all the different images within the firmware
		# This method comes directly from the SDK.  Read through the file in 64 byte chunks, and look for the signature at a certain point in the string
		# Seems kinda scary, as there might be other parts of the file that include this.
		for i in range(0,len(ipmifw),64):
			footer = ipmifw[i:i+64]

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

			curcrc = zlib.crc32(ipmifw[imagestart:imageend]) & 0xffffffff
			imagecrc.append(curcrc)

			if extract:
				print "Dumping 0x%s to 0x%s to data/%s.bin" % (imagestart, imageend, fi.name)
				with open('data/%s.bin' % fi.name.replace("\x00",""),'wb') as f:
					f.write(ipmifw[imagestart:imageend])
				computed_image_checksum = FirmwareImage.computeChecksum(ipmifw[imagestart:imageend])

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
		for imageFooter in re.findall("ATENs_FW(.{8})",ipmifw,re.DOTALL):
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

	def init_image(self, new_image, total_size):
		for i in range(0,total_size):
			new_image.write('\xFF')

	def write_bootloader(self, new_image):
		print "Writing bootloader..."
		with open('data/bootloader.bin','rb') as f:
			new_image.write(f.read())

	def process_image(self, config, imagenum, images, cur_image):
		return cur_image

	def write_image_footer(self, new_image, cur_image, config, configkey, imagenum, base_addr, name):
                load_addr = int(config.get(configkey, 'load_addr'),0)
                exec_addr = int(config.get(configkey, 'exec_addr'),0)
                type = int(config.get(configkey, 'type'),0)

		# Prepare the image footer based on the data
		# we've stored previously
		fi = FirmwareImage()
		fi.imagenum = imagenum
		fi.base_address = base_addr
		fi.load_address = load_addr
		fi.exec_address = exec_addr
		fi.type = type
		fi.name = name
		fi.image_checksum = FirmwareImage.computeChecksum(cur_image)
		fi.length = len(cur_image)

		# Calculate the new checksum..
		fi.footer_checksum = fi.computeFooterChecksum()

		# flash chip breaks data down into 64KB blocks.
		# Footer should be at the end of one of these 
		curblock = int(math.floor(new_image.tell() / 65536))

		curblockend = curblock * 65536

		last_image_end = new_image.tell()

		# If we don't have space to write the footer
		# at the end of the current block, move to the next block
		if curblockend - 61 < last_image_end:
			curblock += 1 

		footerpos = (curblock * 65536) - 61

		new_image.seek(footerpos)

		# And write the footer to the output file
		new_image.write(fi.getRawString())

		return (footerpos, curblockend)

	def prepare_global_footer(self, config, footer, footerpos, curblockend):
		# Hmm... no documentation on where this should be,
		# but in the firmware I have it's been palced right
		# before the last image footer
		# Unsure if that's where it goes, or if it doesn't matter
		# 16 includes 8 padding \xFF's between the global footer
		# and the last image footer
		global_start = footerpos-16
		if global_start < curblockend:
			print "ERROR: Would have written global footer over last image"
			print "Aborting"
			sys.exit(1)

		return global_start

	def write_global_index(self, config, new_image, images):
		pass
 
