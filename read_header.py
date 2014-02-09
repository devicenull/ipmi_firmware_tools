#!/usr/local/bin/python2.7

import re, hashlib, os, io, argparse, sys
from ConfigParser import ConfigParser
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter

cmdparser = argparse.ArgumentParser(description='Read and extract data from SuperMicro IPMI firmware')
cmdparser.add_argument('--extract',action='store_true',help='Extract any detected firmware images')
cmdparser.add_argument('filename',help='Filename to read from')
args = cmdparser.parse_args()

default_ini = """
[flash]
total_size=0

[images]
"""

config = ConfigParser()
config.readfp(io.BytesIO(default_ini))

with open(args.filename,'r') as f:
	ipmifw = f.read()

config.set('flash', 'total_size', len(ipmifw))

try:
	os.mkdir('data')
except OSError:
	pass

print "Read %i bytes" % len(ipmifw)
bootloader = ipmifw[:64040]
bootloader_md5 = hashlib.md5(bootloader).hexdigest()

if bootloader_md5 != "166162c6c9f21d7a710dfd62a3452684":
	print "Warning: bootloader (first 64040 bytes of file) md5 doesn't match.  This parser may not work with a different bootloader"
	print "Expected 166162c6c9f21d7a710dfd62a3452684, got %s" % bootloader_md5
else:
	print "Bootloader md5 matches, this parser will probably work!"

if args.extract:
	print "Dumping bootloader to data/bootloader.bin"
	with open('data/bootloader.bin','w') as f:
		f.write(bootloader)

# I'm not terribly happy with this.  We're reading through a file, looking for the pattern that identifies a block of data.
# Is the controller really doing this on bootup?  The way we're doing it is a horrible abuse of regular expressions!
# We rely on the \xff(9) ... \x9f\xff\xff\xa0 ... \xff(16) signature to check.  Hopefully that doesn't occur otherwise :)

# Looking at some utils included in the SDK (SDK/PKConfig/MDInfo/mdinfo.c) it seems to read in every 64 bytes and only look at the
# signature field.  Might need to switch to that if we have problems with this not finding images
for (part1, part2) in re.findall("\xff{9}(.{40})\x9f\xff\xff\xa0(.{8})\xff{16}",ipmifw,re.DOTALL):
	footer = "%s\x9f\xff\xff\xa0%s" % (part1, part2)

	fi = FirmwareImage()
	fi.loadFromString(footer)


	print "\n"+str(fi)

	imagestart = fi.base_address
	if imagestart > 0x40000000:
		# I'm unsure where this 0x40000000 byte offset is coming from.  Perhaps I'm not parsing the footer correctly?
		imagestart -= 0x40000000

	imageend = imagestart + fi.length

	if args.extract:
		print "Dumping 0x%s to 0x%s to data/%s.bin" % (imagestart, imageend, fi.name)
		with open('data/%s.bin' % fi.name.replace("\x00",""),'w') as f:
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

for imageFooter in re.findall("ATENs_FW(.{8})",ipmifw,re.DOTALL):
	footer = FirmwareFooter()
	footer.loadFromString(imageFooter)

	print "\n"+str(footer)



if args.extract:
	with open('data/image.ini','w') as f:
		config.write(f)
else:
	print "\nConfiguration info:\n"
	config.write(sys.stdout)
