#!/usr/local/bin/python2.7

import os, io, sys, math, zlib
from ConfigParser import ConfigParser
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter

config = ConfigParser()
try:
	config.read('data/image.ini')
except:
	print "Unable to read image configuration"
	os.exit(1)

new_image = open('data/rebuilt_image.bin','w')
new_image.truncate()

for i in range(0,config.getint('flash','total_size')):
	new_image.write("\xFF")

new_image.seek(0)

print "Writing bootloader..."
with open('data/bootloader.bin','r') as f:
	new_image.write(f.read())

images = []
for (imagenum, dummy) in config.items('images'):
	images.append(int(imagenum))

images.sort()

imagecrc = []
for imagenum in images:
	print "Processing image %i"  % imagenum

	configkey = 'image_%i' % imagenum

	# can't use getint, it doesn't support hex
	old_length = int(config.get(configkey, 'length'),0)
	base_addr = int(config.get(configkey, 'base_addr'),0)
	load_addr = int(config.get(configkey, 'load_addr'),0)
	exec_addr = int(config.get(configkey, 'exec_addr'),0)
	name = config.get(configkey, 'name')
	type = int(config.get(configkey, 'type'),0)

        imagestart = base_addr
        if imagestart > 0x40000000:
                # I'm unsure where this 0x40000000 byte offset is coming from.  Perhaps I'm not parsing the footer correctly?
                imagestart -= 0x40000000

	if imagestart < new_image.tell():
		print "ERROR: Previous image was too big, and has overriten data where the current image should begin."
		print "Aborting."
		sys.exit(1)

	# Seek to where this image will start	
	new_image.seek(imagestart)

	with open('data/%s.bin' % name,'r') as img:
		cur_image = img.read()

	# Write the actual image contents
	new_image.write(cur_image)	

	# Compute the CRC32 of this image.  This is used for the global footer, not for each individual footer
	curcrc = zlib.crc32(cur_image) & 0xffffffff
	imagecrc.append(curcrc)

	# Prepare the image footer based on the data we've stored previously
	fi = FirmwareImage()
	fi.imagenum = imagenum
	fi.base_address = base_addr	
	fi.exec_address = exec_addr
	fi.load_address = load_addr
	fi.name = name
	fi.image_checksum = FirmwareImage.computeChecksum(cur_image)
	fi.type = type
	fi.length = len(cur_image)

	# Calculate the new checksum..
	fi.footer_checksum = fi.computeFooterChecksum()

	# flash chip breaks data down into 64KB blocks.  Footer should be at the end of one of these
	curblock = int(math.floor(new_image.tell() / 65536))

	curblockend = curblock * 65536

	last_image_end = new_image.tell()

	# If we don't have space to write the footer at the end of the current block, move to the next block
	if curblockend - 61 < last_image_end:
		curblock += 1

	footerpos = (curblock * 65536) - 61

	new_image.seek(footerpos)

	# And write the footer to the output file
	new_image.write(fi.getRawString())


footer = FirmwareFooter()
footer.rev1 = int(config.get('global','major_version'),0)
footer.rev2 = int(config.get('global','minor_version'),0)
footer.checksum = footer.computeFooterChecksum(imagecrc)

# Hmm... no documentation on where this should be, but in the firmware I have it's been palced right before the last image footer
# Unsure if that's where it goes, or if it doesn't matter
# 16 includes 8 padding \xFF's between the global footer and the last image footer
global_start = footerpos-16
if global_start < curblockend:
	print "ERROR: Would have written global footer over last image"
	print "Aborting"
	sys.exit(1)

# Write the global footer
new_image.seek(global_start)
new_image.write(footer.getRawString())

print "Done!"

