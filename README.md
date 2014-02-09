ipmi_firmware_tools
===================

Various tools for interacting with (SuperMicro) IPMI firmware blobs.

Currently, only firmware using the Winbond WPCM450 controller is supported.  This is pretty standard on the X8 and X9 varients.   Anything using ASpeed AST2400 will not work.

* read_header.py - Given an IPMI firmware image, read throught it and extract all the different parts.  This is done by looking for and decoding the image headers used by the W90P710 bootloader 
* rebuild_image.py - After extracting an image with read_header.py and making changes to the extracted image, this tool will rebuild the image and give you a file that can be flashed to the controller.


Tested:
* <a href="http://www.supermicro.com/products/motherboard/Xeon3000/3400/X8SIE.cfm?IPMI=Y&TYP=LN2">X8SIE-F</a> (SMT_312.bin)
* <a href="http://www.supermicro.com/xeon_3400/Motherboard/X8SIL.cfm?IPMI=Y">X8SIL-F</a> (SMT_313.bin)
* <a href="http://www.supermicro.com/products/motherboard/xeon/c202_c204/x9scl-f.cfm">X9SCL-F</a> (SMT_X9_315.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRi-F.cfm">X9SRi-F</a> (SMT_X9_214.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRL-F.cfm">X9SRL-F</a> (SMT_X9_188.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRG-F.cfm">X9SRG-F</a> (SMT_X9_238.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C600/X9SRW-F.cfm">X9SRW-F</a> (SMT_X9_221.bin)

Not working:
* <a href="http://www.supermicro.com/products/motherboard/Xeon/C220/X10SL7-F.cfm">X8SL7-F</a> (ASpeed) (SMT_X10_123.bin)
* <a href="http://www.supermicro.com/products/motherboard/Xeon3000/X58/X8ST3-F.cfm">X8ST3-F</a> (WPCM450) (X8ST3_204.ima) - This is based on U-Boot 1.1.4

