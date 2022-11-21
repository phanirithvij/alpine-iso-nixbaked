source "$teaiso"/distro/debian.sh
typeset -r populate_rootfs
typeset -r generate_isowork
typeset -r create_rootfs

create_rootfs(){
    if [[ "$codename" == "latest" ]] ; then
        codename=$(wget -O - https://cdimage.ubuntu.com/daily-live/current/  | grep "desktop-amd64.iso" | head -n 1 | sed "s/.*href=\"//g" | sed "s/-.*//g")
    fi
    if ! run debootstrap --arch=$(get_arch $arch) --no-check-gpg --no-merged-usr --exclude="usrmerge" --extractor=ar "$codename" "$rootfs" "$repository" ; then
        cat $rootfs/debootstrap/debootstrap.log
        exit 1
    fi
    echo -e "#!/bin/sh\nexit 101" > "$rootfs"/usr/sbin/policy-rc.d
    chmod +x "$rootfs"/usr/sbin/policy-rc.d
    if [[ "" != "${keyring_package}" ]] ; then
        run_in_chroot apt install ${keyring_package} -yq
    fi
    install "${teaiso}"/misc/usrparse.sh "$rootfs"/tmp/usrparse.sh
    run_in_chroot bash /tmp/usrparse.sh
}

populate_rootfs(){
    run_in_chroot apt update -yq
    run_in_chroot apt full-upgrade -o Dpkg::Options::="--force-confnew" -yq
    run_in_chroot apt install casper -o Dpkg::Options::="--force-confnew" -yq
    mkdir -p "$rootfs"/etc/fonts/
    touch "$rootfs"/etc/fonts/fonts.conf
    mkdir -p "$rootfs"/boot/grub
}

generate_isowork(){
    if [[ -f "$grub_cfg" ]]; then
        cat $grub_cfg > isowork/boot/grub/grub.cfg
    else
        echo "insmod all_video" > isowork/boot/grub/grub.cfg
    fi
    mkdir -p isowork/casper/ || true
    ln -s capser isowork/live
    ln -s . isowork/ubuntu || true
    if [[ -e "filesystem.squashfs" ]]; then
        mv filesystem.squashfs isowork/casper/
        cd isowork/casper; sha512sum filesystem.squashfs > filesystem.sha512
        cd "${workdir}"
    elif [[ -e "filesystem.erofs" ]]; then
        mv filesystem.erofs isowork/casper/
        cd isowork/casper; sha512sum filesystem.erofs > filesystem.sha512
        cd "${workdir}"
    fi
    generate_sig isowork/casper
    ls isowork/boot/ | grep "vmlinuz" | while read line ; do
        echo "menuentry $(distro_name) --class debian {" >> isowork/boot/grub/grub.cfg
        echo "  linux /boot/$line boot=casper ${cmdline}" >> isowork/boot/grub/grub.cfg
        echo "  initrd /boot/$(echo $line | sed s/vmlinuz/initrd.img/g)" >> isowork/boot/grub/grub.cfg
        echo "}" >> isowork/boot/grub/grub.cfg
    done
}
