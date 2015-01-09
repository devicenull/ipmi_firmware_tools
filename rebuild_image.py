#!/usr/bin/python

import os, io, sys, zlib
from ConfigParser import ConfigParser
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter

config = ConfigParser()
try:
	config.read('data/image.ini')
except:
	print "Unable to read image configuration"
	os.exit(1)

if config.get('global','type') == 'aspeed':
	from ipmifw.ASpeed import ASpeed
	firmware = ASpeed()
else:
	from ipmifw.Winbond import Winbond
	firmware = Winbond()

new_image = open('data/rebuilt_image.bin','wb')
new_image.truncate()

# initialize new image
total_size = config.getint('flash','total_size')
firmware.init_image(new_image, total_size)
new_image.seek(0)

# write bootloader
firmware.write_bootloader(new_image)

# prepare list of images to write
images = []
for (imagenum, dummy) in config.items('images'):
	images.append(int(imagenum))

images.sort()

imagecrc = []
# write all images into the firmware file
for imagenum in images:
	print "Processing image %i"  % imagenum

	configkey = 'image_%i' % imagenum

	# can't use getint, it doesn't support hex
	base_addr = int(config.get(configkey, 'base_addr'),0)
	name = config.get(configkey, 'name')

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

	if name[-4:] != '.bin':
		fname = name + '.bin'
	else:
		fname = name
	with open('data/%s' % fname,'rb') as img:
		cur_image = firmware.process_image(config, imagenum, images, img.read())

	# Write the actual image contents
	new_image.write(cur_image)	

	# Compute the CRC32 of this image.  This is used for the global footer, not for each individual footer
	curcrc = zlib.crc32(cur_image) & 0xffffffff
	imagecrc.append(curcrc)

	config.set(configkey, 'curcrc', '0x%x' % curcrc)
	config.set(configkey, 'curlen', '0x%x' % len(cur_image))

	(footerpos, curblockend) = firmware.write_image_footer(new_image, cur_image, config, configkey, imagenum, base_addr, name)

footer = FirmwareFooter()
footer.rev1 = int(config.get('global','major_version'),0)
footer.rev2 = int(config.get('global','minor_version'),0)
footer.footerver = int(config.get('global','footer_version'),0)
footer.checksum = footer.computeFooterChecksum(imagecrc)

# Write the global footer
global_start = firmware.prepare_global_footer(config, footer, footerpos, curblockend)
new_image.seek(global_start)
new_image.write(footer.getRawString())

firmware.write_global_index(config, new_image, images)
 
print "Done, new firmware written to data/rebuild_image.bin"

