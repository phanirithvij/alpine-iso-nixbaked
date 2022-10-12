FROM alpine
RUN apk update
RUN apk add xorriso mtools squashfs-tools git make gcc py3-yaml busybox unzip binutils wget git musl-dev util-linux grub bash
RUN git clone https://gitlab.com/tearch-linux/applications-and-tools/teaiso /tmp/teaiso
RUN cd /tmp/teaiso && make && make install DESTDIR=/
RUN rm -rf /tmp/teaiso
CMD /usr/bin/mkteaiso -p /profile -o /output -w /workdir
