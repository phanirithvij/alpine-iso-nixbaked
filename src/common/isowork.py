import os
from utils import getoutput, run, inf
from datetime import date, datetime
from common import get
import shutil


def create_isowork(settings):
    if not os.path.exists("{}/isowork/boot/grub".format(settings.workdir)):
        os.makedirs("{}/isowork/boot/grub".format(settings.workdir))
    for i in os.listdir("{}/boot".format(settings.rootfs)):
        run("cp -pf {}/boot/{} {}/isowork/boot".format(settings.rootfs,i,settings.workdir))
    
    shutil.copyfile(settings.workdir + "/packages.list", settings.workdir + "/isowork/packages.list")


def create_iso(settings):
    inf("Creating iso file.")
    os.makedirs("{}/isowork/EFI/boot".format(settings.workdir))

    # Copy Necessary Directories
    run("cp -r {}/usr/lib/grub/i386-pc/ {}/isowork/boot/grub/".format(settings.rootfs, settings.workdir))
    run("cp -r {}/usr/lib/grub/i386-efi/ {}/isowork/boot/grub/".format(settings.rootfs, settings.workdir))
    run("cp -r {}/usr/lib/grub/x86_64-efi/ {}/isowork/boot/grub/".format(settings.rootfs, settings.workdir))
    run("cp -r {}/usr/share/grub/themes/ {}/isowork/boot/grub/".format(settings.rootfs, settings.workdir))

    # Generate Bootloaders
    run("grub-mkimage -d {0}/isowork/boot/grub/i386-pc/ -o {0}/isowork/boot/grub/i386-pc/core.img -O i386-pc -p /boot/grub biosdisk iso9660".format(settings.workdir))
    run("cat {0}/isowork/boot/grub/i386-pc/cdboot.img {0}/isowork/boot/grub/i386-pc/core.img > {0}/isowork/boot/grub/i386-pc/eltorito.img".format(settings.workdir))
    run("grub-mkimage -d {0}/isowork/boot/grub/x86_64-efi/ -o {0}/isowork/EFI/boot/bootx64.efi -O x86_64-efi -p /boot/grub iso9660".format(settings.workdir))
    run("grub-mkimage -d {0}/isowork/boot/grub/i386-efi/ -o {0}/isowork/EFI/boot/bootia32.efi -O i386-efi -p /boot/grub iso9660".format(settings.workdir))

    # Generate efi.img
    run("truncate -s 4M {}/isowork/efi.img".format(settings.workdir))
    run("mkfs.vfat -n TEAISO_EFI {}/isowork/efi.img &>/dev/null".format(settings.workdir))
    run("mmd -i {}/isowork/efi.img ::/EFI".format(settings.workdir))
    run("mmd -i {}/isowork/efi.img ::/EFI/boot".format(settings.workdir))
    run("mcopy -i {0}/isowork/efi.img {0}/isowork/EFI/boot/* ::/EFI/boot".format(settings.workdir))
    
    # Miscellaneous
    run("grub-editenv {}/isowork/boot/grub/grubenv set menu_show_once=1".format(settings.workdir))
    
    modification_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-00").replace("-", "")
    run("""xorriso -as mkisofs \
                --modification-date={0} \
                --protective-msdos-label \
                -volid "{1}" \
                -appid "{2}" \
                -publisher "{3}" \
                -preparer "Prepared by TeaISO v{4}" \
                -r -graft-points -no-pad \
                --sort-weight 0 / \
                --sort-weight 1 /boot \
                --grub2-mbr {5}/isowork/boot/grub/i386-pc/boot_hybrid.img \
                -iso_mbr_part_type 0x00 \
                -partition_offset 16 \
                -b boot/grub/i386-pc/eltorito.img \
                -c boot.catalog \
                -no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
                -eltorito-alt-boot \
                -append_partition 2 0xef {5}/isowork/efi.img \
                -e --interval:appended_partition_2:all:: \
                -no-emul-boot \
                -full-iso9660-filenames \
                -iso-level 3 -rock -joliet \
                -o {6} \
                {5}/isowork/""".format(modification_date, get("label"), get("application_id"),
                                       get("publisher"), "2.0", settings.workdir,
                                       settings.output + "/{}-{}-{}.iso".format(get("name"),get("arch"),modification_date)))



def create_squashfs(settings):
    inf("Creating squashfs file.")
    if os.path.exists("{}/filesystem.squashfs".format(settings.workdir)):
        os.unlink("{}/filesystem.squashfs".format(settings.workdir))
    run("mksquashfs {} {}/filesystem.squashfs -comp gzip -wildcards".format(settings.rootfs, settings.workdir))
