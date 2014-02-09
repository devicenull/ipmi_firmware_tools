#!/usr/local/bin/python2.7

import os, io, sys, math
from ConfigParser import ConfigParser
from ipmifw.FirmwareImage import FirmwareImage

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

	# Prepare the image footer based on the data we've stored previously
	fi = FirmwareImage()
	fi.imagenum = imagenum
	fi.base_address = base_addr	
	fi.exec_address = exec_addr
	fi.name = name
	fi.image_checksum = FirmwareImage.computeChecksum(cur_image)
	fi.type = type
	fi.length = len(cur_image)

	# Calculate the new checksum..
	fi.footer_checksum = fi.computeFooterChecksum()

	# flash chip breaks data down into 64KB blocks.  Footer should be at the end of one of these
	curblock = int(math.floor(new_image.tell() / 65536))

	curblockend = curblock * 65536

	# If we don't have space to write the footer at the end of the current block, move to the next block
	if curblockend - 61 < new_image.tell():
		curblock += 1

	footerpos = (curblock * 65536) - 61

	new_image.seek(footerpos)

	# And write the footer to the output file
	new_image.write(fi.getRawString())
