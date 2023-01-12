#!/usr/bin/python
import re, hashlib, zlib, struct
from ipmifw.FirmwareImage import FirmwareImage
from ipmifw.FirmwareFooter import FirmwareFooter


class ASpeed:
    def parse(self, ipmifw, extract, config):
        footer = ipmifw[0x01fc0000:].decode('ISO-8859-1')
        imagenum = 1
        # There's a nice handy block at the end of the file that gives information about all the embedded images!
        for (imagestart, length, checksum, filename) in re.findall("\[img\]: ([0-9a-z]+) ([0-9a-z]+) ([0-9a-z]+) ([0-9a-z\-_.]+)", footer):
            imagestart = int(imagestart,16)
            length = int(length,16)
            checksum = int(checksum,16)

            print("Firmware image: %i Name: %s Base: 0x%x Length: 0x%x CRC32: 0x%x" % (imagenum, filename, imagestart, length, checksum))


            if extract:
                imageend = imagestart + length
                print("Dumping 0x%x to 0x%X to data/%s" % (imagestart, imageend, filename))
                with open('data/%s' % filename,'wb') as f:
                    f.write(ipmifw[imagestart:imageend])

                computed_image_checksum = zlib.crc32(ipmifw[imagestart:imageend]) & 0xffffffff
                if computed_image_checksum != checksum:
                    print("Warning: Image checksum mismatch, footer: 0x%x computed 0x%x" % (checksum, computed_image_checksum))
                else:
                    print("Image checksum matches")

            config.set('images', str(imagenum), 'present')
            configkey = 'image_%i' % imagenum
            config.add_section(configkey)
            config.set(configkey, 'name', str(filename))
            config.set(configkey, 'base_addr', hex(imagestart))
            config.set(configkey, 'length', hex(length))
            config.set(configkey, 'checksum', hex(checksum))

            imagenum += 1

        # Next, find and validate the global footer
        for imageFooter in re.findall(b"ATENs_FW(.{20})", ipmifw, re.DOTALL):
            (rev1, rev2, rootfs_crc, rootfs_len, fwtag1, webfs_crc, webfs_len, fwtag2) = struct.unpack(b"<BB4s4sB4s4sB", imageFooter)
            if fwtag1 != 0x71 or fwtag2 != 0x17:
                print("Error matching footer tags")
            else:
                len2 = config.get('image_2', 'length')
                crc2 = config.get('image_2', 'checksum')
                len4 = config.get('image_4', 'length')
                crc4 = config.get('image_4', 'checksum')

                if rootfs_len.decode('ISO-8859-1') != len2[2:6] or rootfs_crc.decode('ISO-8859-1') != crc2[2:6]:
                    print("Root_fs image info does not match")
                elif webfs_len.decode('ISO-8859-1') != len4[2:6] or webfs_crc.decode('ISO-8859-1') != crc4[2:6]:
                    print("Web_fs image info does not match")
                else:
                    print("Footer OK, rev: %x.%x" % (rev1, rev2))

            config.set('global', 'major_version', str(rev1))
            config.set('global', 'minor_version', str(rev2))

    def init_image(self, new_image, total_size):
        # Aspeed image has some parts filled with nulls
        if total_size < 0x1F40000:
            print("Unexpected ASpeed image size")
            os.exit(1)
        # space for uboot bootloader
        for i in range(0,0x100000):
            new_image.write(b'\xFF')
        # nvram block, not referenced in the footer
        for i in range(0x100000,0x400000):
            new_image.write(b'\x00')
        # root_fs, kernel and web_fs
        for i in range(0x400000,0x1F40000):
            new_image.write(b'\xFF')
        # bootloader env aka footer
        for i in range(0x1F40000,total_size):
            new_image.write(b'\x00')

    def write_bootloader(self, new_image):
        pass

    def process_image(self, config, imagenum, images, cur_image):
        # ASpeed seems to place global footer right after the last image
        # The size contains also part of the footer, so we extract it
        # But if the image is re-packed, that part is lost
        # so we need to check and add it, if needed
        if imagenum == images[-1]:
            if cur_image[-10:-2] != b"ATENs_FW":
                footer = FirmwareFooter()
                footer.rev1 = int(config.get('global','major_version'),0)
                footer.rev2 = int(config.get('global','minor_version'),0)
                footer.footerver = int(config.get('global','footer_version'),0)
                footer.rootfs_nfo = "00000000"
                footer.webfs_nfo = "00000000"
                return cur_image + footer.getRawString()[:10]
        return cur_image

    def write_image_footer(self, new_image, cur_image, config, configkey, imagenum, base_addr, name):
        # no image footer for ASpeed, but check for changes
        curcrc = int(config.get(configkey, 'curcrc'), 0)
        if curcrc == int(config.get(configkey, 'checksum'), 0):
            print("  Image unchanged")
        else:
            print("  Image modified")

        return (new_image.tell(), None)

    def prepare_global_footer(self, config, footer, footerpos, curblockend):
        # ASpeed specific parameters
        crc2 = config.get('image_2', 'curcrc')
        len2 = config.get('image_2', 'curlen')
        crc4 = config.get('image_4', 'curcrc')
        len4 = config.get('image_4', 'curlen')
        footer.rootfs_nfo = '%4s%4s' % (crc2[2:6], len2[2:6])
        footer.webfs_nfo = '%4s%4s' % (crc4[2:6], len4[2:6])
        # ASpeed seems to place global footer right after the last image
        return footerpos - 10

    def write_global_index(self, config, new_image, images):
        # add ASpeed specific index
        new_image.seek(0x1FC0000)
        for imagenum in images:
            configkey = 'image_%i' % imagenum
            img_base = int(config.get(configkey, 'base_addr'),0)
            img_len = int(config.get(configkey, 'curlen'),0)
            img_crc = int(config.get(configkey, 'curcrc'),0)
            img_name = config.get(configkey, 'name')

            new_image.write(b'[img]: ')
            new_image.write(("%x %x %x %s" % (img_base, img_len, img_crc, img_name)).encode('ISO-8859-1'))
        new_image.write(b'[end]')

