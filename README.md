ipmi_firmware_tools
===================

Various tools for interacting with (SuperMicro) IPMI firmware blobs.

Firmware using the Winbond WPCM450 controller is supported (pretty standard on the X8 and X9 variants), as well as ASpeed AST2400 controller (common on X10 boards).

* read_header.py - Given an IPMI firmware image, read throught it and extract all the different parts.  This is done by looking for and decoding the image headers used by the bootloader 
* rebuild_image.py - After extracting an image with read_header.py and making changes to the extracted image, this tool will rebuild the image and give you a file that can be flashed to the controller.


Tested:
* <a href="http://www.supermicro.com/products/motherboard/Xeon3000/3400/X8SIE.cfm?IPMI=Y&TYP=LN2">X8SIE-F</a> (SMT_312.bin)
* <a href="http://www.supermicro.com/xeon_3400/Motherboard/X8SIL.cfm?IPMI=Y">X8SIL-F</a> (SMT_313.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRi-F.cfm">X9SRi-F</a> (SMT_X9_214.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRL-F.cfm">X9SRL-F</a> (SMT_X9_188.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRG-F.cfm">X9SRG-F</a> (SMT_X9_238.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRW-F.cfm">X9SRW-F</a> (SMT_X9_221.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10drt-h.cfm">X10SLL-F</a> (ASpeed) (SMT_X10_135.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c220/x10slh-f.cfm">X10SLH-F</a> (ASpeed) (SMT_X10_142.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c220/x10sle-df.cfm">X10SLE-DF</a> (ASpeed) (SMT_X10_143.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c220/x10sla-f.cfm">X10SLA-F</a> (ASpeed) (SMT_X10_150.bin)
* <a href="http://www.supermicro.com/products/motherboard/atom/x10/a1sam-2550f.cfm">A1SAM-2550F</a> (ASpeed) (SMT_X10_154.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10ddw-i.cfm">X10DDW-i</a> (ASpeed) (SMT_X10_159.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10drt-p.cfm">X10DRT-P</a> (ASpeed) (SMT_X10_164.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10drh-c.cfm">X10DRH-C</a> (ASpeed) (SMT_X10_166.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10dri.cfm">X10DRi</a> (ASpeed) (SMT_X10_167.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10drg-h.cfm">X10DRG-H</a> (ASpeed) (SMT_X10_169.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10srg-f.cfm">X10SRG-F</a> (ASpeed) (SMT_X10_170.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10dru-x.cfm">X10DRU-X</a> (ASpeed) (SMT_X10_171.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10drw-i.cfm">X10DRW-i</a> (ASpeed) (SMT_X10_172.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10ddw-in.cfm">X10DDW-iN</a> (ASpeed) (SMT_X10_174.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10dru-xll.cfm">X10DRU-XLL</a> (ASpeed) (SMT_X10_175.bin)
* <a href="http://www.supermicro.com/products/motherboard/atom/x10/a1sai-2550f.cfm">A1SAi-2550F</a> (ASpeed) (SMT_X10_176.bin)
* <a href="http://www.supermicro.com/products/motherboard/core/x99/c7x99-oce-f.cfm">C7X99-OCE-F</a> (ASpeed) (SMT_X10_177.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10dru-i_.cfm">X10DRU-i+</a> (ASpeed) (SMT_X10_180.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x10drt-h.cfm">X10DRT-H</a> (ASpeed) (X10_IPMI_FW_1.13.bin)

Not working:
* <a href="http://www.supermicro.com/products/motherboard/xeon/c202_c204/x9scl-f.cfm">X9SCL-F</a> (SMT_X9_315.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c600/x9dax-7f.cfm">X9DAX-7F</a> (SMT_X9_331.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c220/x10sld-hf.cfm">X10SLD-HF</a> (ASpeed) (SMT_X10_109.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon3000/X58/X8ST3-F.cfm">X8ST3-F</a> (WPCM450) (X8ST3_204.ima) - This is based on U-Boot 1.1.4

Winbond bootloader
------------------

0x0 - 0xfa40 - This is the standard WinBond bootloader, aka "WPCM450 Boot Loader [ Version:1.0.14 ]".  This is shared between virtually all X8 and X9 the firmware.

ASpeed nvram
------------

ASpeed firmware does not have bootloader specific part, it has uBoot bootloader referenced in the image footer. On the other hand, it has a part of image starting at offset 0x00100000 and 0x00300000 bytes long, which is described as nvram in the X10 SDK files. In all examined X10 firmwares, this part was always filled with zeroes.

Image footer Winbond
--------------------
64 bytes total.  To find these, read through the file in 64 byte chunks and look for a valid signature string in the correct position.  Seriously, this is how the "offical" tools do it.

The actual footer contents look like this:

<pre>
12 bytes - padding, value does not matter, though it's usually 0xFF
4 bytes - image number, these are usually between 2 and 5.  Image number 0 is reserved for special things, and is never present
4 bytes - base address, this determines where the image starts in the file.  I've noticed these are too big by 0x40000000, though I'm not sure why
4 bytes - load address, the bootloader will copy the image to memory starting at this location
4 bytes - exec address, if this image is to be executed, this is where execution will begin
16 bytes - image name, padded with 0x00
4 bytes - image checksum, this is computed using some strange method.  See FirmwareImage.computeChecksum
4 bytes - signature, this should be \xa0\xff\xff\x9f and is how you recongize an image
4 bytes - type, bitmask controlling what the bootloader does with this image.  See FirmwareImage.IMAGE_*
4 bytes - footer checksum, this is computed using all the preceeding fields (excluding the padding).  Same method as the image checksum
</pre>

Image footer ASpeed
--------------------
ASpeed is a bit smarter, there is an "index" block at offsett 0x01FC0000 describing all images stored in the firmware:

<pre>
text - "[img]: "
hexadecimal number in ascii - image start
hexadecimal number in ascii - image length
hexadecimal number in ascii - image checksum
text - image file name
</pre>

File footer 1
-------------
This appears once in the file.  This particular format is used by the older firmware versions (seems to be anything before 3.00)

<pre>
ATENs_FW - string, this is how you find the footer
1 byte - integer, firmware major version
1 byte - integer, firmware minor version
</pre>

File footer 2
-------------
Again, this appears only once in the file.  This particular format is used by the newer firmware (> 3.00)

<pre>
ATENs_FW - string
1 byte - integer, firmware major version
1 byte - integer, firmware minor version
0x71 - constant, helps you find the footer
4 bytes - crc32 of all image blocks.  To find this, calculate the crc32 of each image data block.  Concatenate the raw values of all of them (in order by image number), and take the crc32 of that
0x17 - constant, helps you find the footer
</pre>

File footer 3
-------------
Used in ASpeed firmwares. Extension to version 2 above.

<pre>
ATENs_FW - string
1 byte - integer, firmware major version
1 byte - integer, firmware minor version
4 bytes - string, upper part of rootfs checksum
4 bytes - string, upper part of rootfs length
0x71 - constant, helps you find the footer
4 bytes - string, upper part of webfs checksum
4 bytes - string, upper part of webfs length
0x17 - constant, helps you find the footer
</pre>

