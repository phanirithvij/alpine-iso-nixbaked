FROM nixos/nix as nixer
RUN nix-channel --update
RUN nix-build -A nixos-install-tools '<nixpkgs>'

FROM alpine
COPY --from=nixer /nix/store /nix/store
RUN apk update
RUN apk add git make gcc git musl-dev
RUN apk add xorriso mtools squashfs-tools py3-yaml busybox unzip binutils wget
RUN apk add grub bash perl tar zstd coreutils dosfstools e2fsprogs util-linux
# RUN apk add grub-efi grub-bios breeze-grub
#RUN git clone https://gitlab.com/tearch-linux/applications-and-tools/teaiso /tmp/teaiso
COPY . /tmp/teaiso
RUN cd /tmp/teaiso && make && make install DESTDIR=/
RUN apk del git gcc git musl-dev
RUN rm -rf /tmp/teaiso
RUN mkdir -p /profile /output
CMD /usr/bin/mkteaiso -p /profile -o /output
