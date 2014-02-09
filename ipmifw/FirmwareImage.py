
import struct

class FirmwareImage:
	# indicates the image will be used during boot
	IMAGE_ACTIVE = 0x01
	# indicates it should be copied from flash to ram on boot.  Copies *from* the load address to the base address, but only if it's active
	IMAGE_COPY2RAM = 0x02
	# indicates control should be passed to the image (how? I dunno)
	IMAGE_EXEC = 0x04
	# indicates this is a filesystem image
	IMAGE_FILE = 0x08
	# indicates the image is compressed.  Supposedly via ZIP
	IMAGE_COMPRESSED = 0x10

	# This data comes from the "W90P710 Bootloader Users Manual" (find it yourself, I'm not allowed to distribute it)
	footer_format = "<5I16s4I"

	# This signature should be valid if this is a valid firmware image
	correct_signature = struct.unpack('<I',"\x9f\xff\xff\xa0")[0]

        # I largely don't have any idea how or why this works.  It was basically just coding by trival and error.
        # I'm unsure of why they used this, versus something more standard
        @staticmethod
        def computeChecksum(data):
                cksum = 0xffffffff

                for i in range(0,len(data)):
                        char = ord(data[i])

                        cksum -= char << ((i%4)*8)

                        if cksum < 0:
                                cksum &= 0xffffffff
                                cksum -= 1

                return cksum

	def __init__(self):
		self.imagenum = 0
		self.base_address = 0
		self.length = 0
		self.load_address = 0
		self.exec_address = 0
		self.name = 0
		self.image_checksum = 0
		self.signature = struct.unpack('<I',"\x9f\xff\xff\xa0")[0]
		self.type = 0
		self.footer_checksum = 0
		
	def loadFromString(self,footer): 
		(self.imagenum, self.base_address, self.length, self.load_address, self.exec_address, self.name, self.image_checksum, self.signature, self.type, self.footer_checksum) = struct.unpack(FirmwareImage.footer_format,footer)
		self.name = self.name.replace("\x00","")

	def getRawString(self):
		contents = struct.pack("<5I16s4I",self.imagenum, self.base_address, self.length, self.load_address, self.exec_address, self.name, self.image_checksum, self.signature, self.type, self.footer_checksum)
		return "\xff\xff\xff\xff\xff\xff\xff\xff\xff"+contents+"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"

	def isValid(self):
		return self.signature == FirmwareImage.correct_signature

	# The footer checksum is only the 48 bytes of actual data (excludes the \xff padding, and the checksum itself)
	def computeFooterChecksum(self):
		footer_data = struct.pack("<5I16s3I",self.imagenum, self.base_address, self.length, self.load_address, self.exec_address, self.name, self.image_checksum, self.signature, self.type)
		return FirmwareImage.computeChecksum(footer_data)


	def __str__(self):
        	flag_desc = []
        	if self.type & FirmwareImage.IMAGE_ACTIVE:
                	flag_desc.append('active')
        	if self.type & FirmwareImage.IMAGE_COPY2RAM:
                	flag_desc.append('copy2ram')
        	if self.type & FirmwareImage.IMAGE_EXEC:
                	flag_desc.append('exec')
        	if self.type & FirmwareImage.IMAGE_FILE:
                	flag_desc.append('file')
	        if self.type & FirmwareImage.IMAGE_COMPRESSED:
       	        	flag_desc.append('compressed')

		description = "Firmware image: %i Name: %s Base: 0x%x Length: 0x%x (%i) Load: 0x%x Exec: 0x%x Image Checksum: 0x%x Signature: 0x%x Type: %s (0x%x) Footer Checksum: 0x%x" % (self.imagenum, self.name, self.base_address, self.length, self.length, self.load_address, self.exec_address, self.image_checksum, self.signature, ', '.join(flag_desc), self.type, self.footer_checksum)

		computed_footer_checksum = self.computeFooterChecksum()

		if self.footer_checksum == computed_footer_checksum:
			description += " * footer checksum matches"
		else:
			description += " * footer checksum mismatch, expected 0%x" % computed_footer_checksum

		return description		

