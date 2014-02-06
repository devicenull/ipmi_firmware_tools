
# some example headers, not used for anything but reference
headers = [
	"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x02\x00\x00\x00\x00\x00\x18\x40\x00\xe0\x7b\x00\x00\x00\xd0\x00\x00\x00\xd0\x00\x31\x73\x74\x46\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0a\x2c\xc1\xae\x9f\xff\xff\xa0\x08\x00\x00\x00\xc7\x80\x96\x27\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
	"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x03\x00\x00\x00\x00\x00\x98\x40\xa8\x2a\x11\x00\x00\x80\x00\x00\x00\x80\x00\x00\x6b\x65\x72\x6e\x65\x6c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x23\xf5\xcc\x9c\x9f\xff\xff\xa0\x17\x00\x00\x00\xaa\x0e\x16\x13\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
	"\x29\x9f\x17\xff\xff\xff\xff\xff\xff\xff\xff\xff\x04\x00\x00\x00\x00\x00\xb8\x40\x00\x10\x1e\x00\x00\x00\xd0\x00\x00\x00\xd0\x00\x32\x6e\x64\x46\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xac\x1c\x9c\x9a\x9f\xff\xff\xa0\x08\x00\x00\x00\x22\x65\x89\x3b\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
]


# indicates the image must be processed? at boot time
IMAGE_ACTIVE = 0x01
# indicates it should be copied from flash to ram on boot.  Copies *from* the load address to the base address, but only if it's active
IMAGE_COPY2RAM = 0x02
# indicates control should be passed to the image (how? I dunno)
IMAGE_EXEC = 0x04
# indicates this is a filesystem image
IMAGE_FILE = 0x08
# indicates the image is compressed.  Supposedly via ZIP
IMAGE_COMPRESSED = 0x10

import struct, re, hashlib

with open('SMT_313.bin','r') as f:
	ipmifw = f.read()

print "Read %i bytes" % len(ipmifw)
bootloader = ipmifw[:64040]
bootloader_md5 = hashlib.md5(bootloader).hexdigest()

if bootloader_md5 != "166162c6c9f21d7a710dfd62a3452684":
	print "Warning: bootloader (first 64040 bytes of file) md5 doesn't match.  This parser may not work with a different bootloader"
	print "Expected 166162c6c9f21d7a710dfd62a3452684, got %s" % bootloader_md5
	print "Dumping bootloader to bootloader.bin and continuing..."
	with open('bootloader.bin','w') as f:
		f.write(bootloader)
else:
	print "Bootloader md5 matches, this parser will probably work!"


# This data comes from the "W90P710 Bootloader Users Manual" (find it yourself, I'm not allowed to distribute it)
#
# I'm not terribly happy with this.  We're reading through a file, looking for the pattern that identifies a block of data.
# Is the controller really doing this on bootup?  The way we're doing it is a horrible abuse of regular expressions!
# We rely on the \xff(9) ... \x9f\xff\xff\xa0 ... \xff(16) signature to check.  Hopefully that doesn't occur otherwise :)
for (part1, part2) in re.findall("\xff{9}(.{40})\x9f\xff\xff\xa0(.{8})\xff{16}",ipmifw,re.DOTALL):
	header = "%s\x9f\xff\xff\xa0%s" % (part1, part2)

	(imagenum, base_addr, length, load_address, exec_address, name, image_checksum, signature, type, footer_checksum) = struct.unpack("<5I16s4I",header)

	flag_desc = []
	if type & IMAGE_ACTIVE:
		flag_desc.append('active')
	if type & IMAGE_COPY2RAM:
		flag_desc.append('copy2ram')
	if type & IMAGE_EXEC:
		flag_desc.append('exec')
	if type & IMAGE_FILE:
		flag_desc.append('file')
	if type & IMAGE_COMPRESSED:
		flag_desc.append('compressed')

	print "Image: %i Name: %s Base: 0x%x Length: 0x%x (%i) Load: 0x%x Exec: 0x%x Image Checksum: 0x%x Signature: 0x%x Type: %s (0x%x) Footer Checksum: 0x%x" % (imagenum, name, base_addr, length, length, load_address, exec_address, image_checksum, signature, ', '.join(flag_desc), type, footer_checksum)


