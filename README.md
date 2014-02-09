ipmi_firmware_tools
===================

Various tools for interacting with (SuperMicro) IPMI firmware blobs

* read_header.py - Given an IPMI firmware image, read throught it and extract all the different parts.  This is done by looking for and decoding the image headers used by the W90P710 bootloader 
* rebuild_image.py - After extracting an image with read_header.py and making changes to the extracted image, this tool will rebuild the image and give you a file that can be flashed to the controller.
