FROM ubuntu:disco
MAINTAINER Jesse Vincent <jesse@keyboard.io>
LABEL Description="Minimal KiCad image based on Ubuntu"

ADD kicad-ppa.pgp .
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
        apt-get -y update && \
        apt-get -y install gnupg2 && \
        echo 'deb http://ppa.launchpad.net/js-reynaud/kicad-5.1/ubuntu disco main' >> /etc/apt/sources.list && \
        apt-key add kicad-ppa.pgp && \
        apt-get -y update && apt-get -y install --no-install-recommends kicad kicad-footprints kicad-symbols kicad-packages3d && \
        apt-get -y purge gnupg2 && \
        apt-get -y autoremove && \
        rm -rf /var/lib/apt/lists/* && \
        rm kicad-ppa.pgp

COPY eeschema/requirements.txt .
RUN apt-get -y update && \
    apt-get install -y python python-pip xvfb recordmydesktop xdotool xclip && \
    pip install -r requirements.txt && \
    rm requirements.txt && \
    apt-get -y remove python-pip && \
    rm -rf /var/lib/apt/lists/*

# Use a UTF-8 compatible LANG because KiCad 5 uses UTF-8 in the PCBNew title
# This causes a "failure in conversion from UTF8_STRING to ANSI_X3.4-1968" when
# attempting to look for the window name with xdotool.
ENV LANG C.UTF-8

COPY . /usr/lib/python2.7/dist-packages/kicad-automation

# Copy default configuration and fp_lib_table to prevent first run dialog
COPY ./config/* /root/.config/kicad/

# Copy the installed global symbol and footprint so projcts built with stock
# symbols and footprints don't break
CMD ["cp","/usr/share/kicad/template/sym-lib-table","/root/.config/kicad/"]
CMD ["cp","/usr/share/kicad/template/fp-lib-table","/root/.config/kicad/"]

