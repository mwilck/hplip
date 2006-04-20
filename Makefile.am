#
#  Makefile.am - hplip automake input file
# 
#  (c) 2004-2005 Copyright Hewlett-Packard Development Company, LP
#

SUBDIRS = . prnt/hpijs
INCLUDES = -Iprnt/hpijs -Iip

hplipdir = $(datadir)/hplip
rundir = /var/run

docdir = $(datadir)/doc/$(distdir)
doc_DATA =  hplip_readme.html hplip_overview.png COPYING

dist_hplip_DATA = $(doc_DATA) hplip.conf
dist_hplip_SCRIPTS = hpssd.py __init__.py hplip.sh

cmddir = $(hplipdir)
dist_cmd_SCRIPTS = align.py info.py print.py toolbox.py clean.py colorcal.py photo.py unload.py testpage.py makeuri.py check.py fab.py levels.py \
    sendfax.py setup.py

cupsdir = $(CUPS_BACKEND_PATH)
cupsppddir = $(CUPS_PPD_PATH)
hpppddir = $(datadir)/ppd/HP

# hp backend.
cups_PROGRAMS = hp
hp_SOURCES = backend/hp/hp.c 
hp_LDADD = libhplip-api.la

# hpiod
sbin_PROGRAMS = hpiod
hpiod_SOURCES = io/hpiod/hpiod.cpp io/hpiod/channel.cpp io/hpiod/device.cpp io/hpiod/mlc.cpp io/hpiod/system.cpp io/hpiod/jddevice.cpp io/hpiod/jetdirect.cpp \
    io/hpiod/udevice.cpp io/hpiod/uppdevice.cpp io/hpiod/ppdevice.cpp io/hpiod/pp.cpp io/hpiod/channel.h io/hpiod/device.h io/hpiod/hpiod.h io/hpiod/mlc.h \
    io/hpiod/system.h io/hpiod/dot4.cpp io/hpiod/ppdot4.cpp io/hpiod/dot4.h io/hpiod/list.h io/hpiod/usbext.c io/hpiod/usbext.h io/hpiod/comp.cpp

# base
basedir = $(hplipdir)/base

dist_base_SCRIPTS = base/maint.py base/codes.py base/g.py base/pml.py base/status.py  base/async.py \
    base/__init__.py base/mfpdtf.py base/utils.py base/async_qt.py base/kirbybase.py base/service.py \
    base/device.py base/logger.py base/msg.py base/slp.py base/exif.py base/strings.py base/magic.py \
    base/imagesize.py base/subproc.py

# fax
faxdir = $(hplipdir)/fax
dist_fax_SCRIPTS = fax/fax.py fax/__init__.py fax/coverpages.py
hpfaxdir = $(hplipdir)/fax/backend
dist_hpfax_SCRIPTS = fax/backend/hpfax.py
faxppddir = $(hplipdir)/fax/ppd
dist_faxppd_DATA = fax/ppd/HP-Fax-hplip.ppd

# ptest
noinst_PROGRAMS = ptest
ptest_SOURCES = pcard/ptest.c pcard/ptest.h pcard/fat.c pcard/fat.h 
ptest_LDADD = libhplip-api.la

# data
xmldir = $(hplipdir)/data/xml
imagesdir = $(hplipdir)/data/images
pcldir = $(hplipdir)/data/pcl
ldldir = $(hplipdir)/data/ldl
psdir = $(hplipdir)/data/ps
icondir = $(hplipdir)/data
dist_ps_DATA = data/ps/testpage.ps.gz data/ps/clean_page.pdf.gz
#dist_xml_DATA = data/xml/models.xml
dist_xml_DATA = data/xml/*.xml
dist_images_DATA = data/images/*
dist_pcl_DATA = data/pcl/align1_8xx.pcl.gz data/pcl/align1_9xx.pcl.gz data/pcl/align2_8xx.pcl.gz data/pcl/align3_8xx.pcl.gz data/pcl/align4_8xx.pcl.gz \
    data/pcl/align5_8xx.pcl.gz data/pcl/align2_9xx.pcl.gz data/pcl/align3_9xx.pcl.gz data/pcl/align4_450.pcl.gz data/pcl/align6_450.pcl.gz \
    data/pcl/colorcal1_450.pcl.gz data/pcl/colorcal2_450.pcl.gz data/pcl/crbcal.pcl.gz data/pcl/crcaldone.pcl.gz data/pcl/crcbcal.pcl.gz data/pcl/crccal.pcl.gz \
    data/pcl/crcpcal.pcl.gz data/pcl/crpcal.pcl.gz 
dist_ldl_DATA = data/ldl/cb2pcal.ldl.gz data/ldl/cb2pcal_done.ldl.gz data/ldl/cbbcal.ldl.gz data/ldl/cbccal.ldl.gz data/ldl/cbccal_done.ldl.gz data/ldl/cbcpcal.ldl.gz \
    data/ldl/cbpcal.ldl.gz

# pcard 
pcarddir = $(hplipdir)/pcard
pcardextdir = $(hplipdir)/pcard/pcardext
dist_pcard_SCRIPTS = pcard/__init__.py pcard/photocard.py
dist_noinst_SCRIPTS = pcard/pcardext/setup.py pcard/pcardext/pcardext.c \
    prnt/cupsext/setup.py prnt/cupsext/cupsext.c 
noinst_DATA = build-pcardext build-cupsext

# prnt
prntdir = $(hplipdir)/prnt
cupsextdir = $(hplipdir)/prnt/cupsext
dist_prnt_SCRIPTS = prnt/cups.py prnt/__init__.py prnt/ldl.py prnt/pcl.py prnt/colorcal.py 
#noinst_SCRIPTS = prnt/cupsext/setup.py prnt/cupsext/cupsext.c build-cupsext
#noinst_DATA = build-cupsext

# scan
scandir = $(hplipdir)/scan
dist_scan_SCRIPTS = scan/__init__.py

# ip library
lib_LTLIBRARIES = libhpip.la libsane-hpaio.la
libhpip_la_SOURCES = ip/xconvolve.c ip/xfax.c ip/xgrayout.c ip/xjpg_dct.c ip/xjpg_fix.c ip/xpad.c ip/xrotate.c ip/xskel.c ip/xtiff.c \
    ip/ipmain.c ip/xchgbpp.c ip/xcrop.c ip/xgamma.c ip/xjpg_dec.c ip/xjpg_huf.c ip/xpcx.c ip/xsaturation.c ip/xtable.c ip/xtonemap.c \
    ip/xbi2gray.c ip/xcolrspc.c ip/xfakemono.c ip/xgray2bi.c ip/xinvert.c ip/xjpg_enc.c ip/xmatrix.c ip/xpnm.c ip/xscale.c ip/xthumb.c ip/xyxtract.c \
    ip/hpip.h ip/ipdefs.h ip/xform.h ip/xjpg_dct.h ip/xjpg_huf.h ip/xjpg_mrk.h
libhpip_la_LDFLAGS = -version-info 0:1:0

# sane backend
BASENAME=sane-hpaio
MAJORVER=1
MINORVER=0
AGEVER=0
SONOVER=lib$(BASENAME).so
SOSHORT=$(SONOVER).$(MAJORVER)
SOLONG=$(SOSHORT).$(MINORVER).$(AGEVER)
sanedir = $(libdir)/sane
#lib_LTLIBRARIES = libsane-hpaio.la
libsane_hpaio_la_SOURCES = scan/sane/hpaio.c scan/sane/mfpdtf.c scan/sane/pml.c scan/sane/scl.c scan/sane/io.c scan/sane/hpaio.h scan/sane/pml.h scan/sane/saneopts.h scan/sane/io.h \
      scan/sane/mfpdtf.h scan/sane/sane.h scan/sane/scl.h scan/sane/tables.h
libsane_hpaio_la_LDFLAGS = -version-info $(MAJORVER):$(MINORVER):$(AGEVER) 
# The following is a interlibrary dependency that must be compiled first.
libsane_hpaio_la_LIBADD = libhpip.la libhplip-api.la

# api library
noinst_LTLIBRARIES = libhplip-api.la
libhplip_api_la_SOURCES = prnt/hpijs/hplip_api.c prnt/hpijs/hplip_api.h

# ui
uidir = $(hplipdir)/ui
dist_ui_SCRIPTS = ui/alignform.py \
    ui/colorcalform_base.py ui/colorcalform.py ui/coloradjform_base.py ui/coloradjform.py ui/devmgr4_base.py ui/devmgr4.py \
    ui/__init__.py ui/loadpaperform_base.py ui/loadpaperform.py \
    ui/paperedgealignform_base.py ui/paperedgealignform.py \
    ui/settingsdialog_base.py ui/settingsdialog.py ui/aligntype6form1.py ui/aligntype6form1_base.py ui/aligntype6form2_base.py \
    ui/aligntype6form2.py ui/nodevicesform_base.py ui/nodevicesform.py ui/unloadform.py ui/unloadform_base.py \
    ui/imagepropertiesdlg_base.py ui/imagepropertiesdlg.py ui/choosedevicedlg.py ui/chooseprinterdlg.py \
    ui/aboutdlg.py ui/aboutdlg_base.py ui/waitform.py ui/waitform_base.py ui/cleaningform_base.py ui/cleaningform.py \
    ui/cleaningform2_base.py ui/cleaningform2.py ui/colorcalform2_base.py ui/colorcalform2.py ui/colorcal4form.py \
    ui/colorcal4form_base.py ui/colorcal4form_base.ui ui/printerform.py ui/printerform_base.ui ui/printerform_base.py \
    ui/faxaddrbookgroupsform_base.py ui/faxaddrbookgroupeditform_base.py ui/faxaddrbookform_base.py \
    ui/faxaddrbookform.py ui/faxaddrbookeditform_base.py ui/align10form.py ui/align10form_base.py \
    ui/informationform_base.py ui/informationform.py ui/supportform_base.py ui/supportform.py \
    ui/faxsendjobform_base.py ui/faxsendjobform.py ui/faxsettingsform_base.py ui/faxsettingsform.py \
    ui/coverpageform_base.py ui/coverpageform.py

dist_noinst_DATA = ui/unloadform_base.ui ui/colorcalform2_base.ui ui/settingsdialog_base.ui ui/aligntype6form1_base.ui \
    ui/aboutdlg_base.ui ui/imagepropertiesdlg_base.ui ui/paperedgealignform_base.ui ui/aligntype6form2_base.ui \
    ui/nodevicesform_base.ui ui/cleaningform_base.ui ui/colorcalform_base.ui ui/devmgr4_base.ui ui/loadpaperform_base.ui \
    ui/cleaningform2_base.ui ui/waitform_base.ui ui/coloradjform_base.ui ui/faxaddrbookeditform_base.ui \
    ui/faxaddrbookform_base.ui ui/faxaddrbookgroupeditform_base.ui ui/faxaddrbookgroupsform_base.ui \
    ui/align10form_base.ui ui/informationform_base.ui ui/supportform_base.ui \
    plugins/powersettingsdialog_base.ui ui/faxsendjobform_base.ui ui/faxsettingsform_base.ui ui/coverpageform_base.ui

# ui plugins
pluginsdir = $(hplipdir)/plugins
dist_plugins_SCRIPTS = plugins/dj450.py plugins/__init__.py plugins/powersettings.py plugins/powersettingsdialog.py \
    plugins/powersettingsdialog_base.py plugins/Deskjet_460.py

build-pcardext: 
	cd pcard/pcardext; \
	$(PYTHON) setup.py build

build-cupsext: 
	cd prnt/cupsext; \
	$(PYTHON) setup.py build

install-exec-hook: test-destdir
#
#       Do full install if not rpm_install.
	if [ "$(rpm_install)" = "no" ]; then \
	   ln -sf ../$(SOLONG) $(DESTDIR)$(sanedir)/$(SONOVER); \
	   ln -sf ../$(SOLONG) $(DESTDIR)$(sanedir)/$(SOSHORT); \
	   ln -sf ../$(SOLONG) $(DESTDIR)$(sanedir)/$(SOLONG); \
	   if [ -f $(DESTDIR)/etc/sane.d/dll.conf ]; then \
	      if ! grep ^hpaio $(DESTDIR)/etc/sane.d/dll.conf >/dev/null 2>/dev/null ; then \
	         echo "Adding hpaio entry to /etc/sane.d/dll.conf." ; \
	         echo hpaio >>$(DESTDIR)/etc/sane.d/dll.conf ; \
	      fi \
	   fi \
	fi

install-data-hook: test-destdir
	if [ "$(ICON_FILE)" = "hplip.desktop" ]; then \
	   echo -e "[Desktop Entry]" > $(srcdir)/$(ICON_FILE); \
	   echo -e "Version=0.6" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Type=Application" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Name=HP Device Manager" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "GenericName=HP Device Manager" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Comment=View device status, ink levels and perform maintenance." >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Exec=$(datadir)/hplip/toolbox" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Icon=$(imagesdir)/HPmenu.png" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Terminal=false" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "Categories=Application;Utility;" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "X-KDE-StartupNotify=false" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "StartupNotify=false" >> $(srcdir)/$(ICON_FILE); \
	fi
	if [ "$(ICON_FILE)" = "hplip" ]; then \
	   echo -e "?package(xbase):command=\"$(datadir)/hplip/toolbox\" icon=\"$(imagesdir)/HPmenu.png\" \\" > $(srcdir)/$(ICON_FILE); \
	   echo -e "                needs=\"X11\" section=\"Application/Utility\" title=\"HPLIP\" \\" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "                longtitle=\"HPLIP Device Manager\" \\" >> $(srcdir)/$(ICON_FILE); \
	   echo -e "                mimetypes=\"\" accept_url=\"false\" multiple_files=\"true\"" >> $(srcdir)/$(ICON_FILE); \
	fi
	if [ "$(ICON_FILE)" != "" ]; then \
	   $(INSTALL_DATA)  $(srcdir)/$(ICON_FILE) $(DESTDIR)$(icondir); \
	   rm -f $(srcdir)/$(ICON_FILE); \
	fi
#
#       Do full install if not rpm_install.
	if [ "$(rpm_install)" = "no" ]; then \
	   if [ "$(ICON_FILE)" != "" ]; then \
	      if [ -d $(DESTDIR)$(ICON_PATH) ]; then \
	         ln -sf $(icondir)/$(ICON_FILE) $(DESTDIR)$(ICON_PATH)/$(ICON_FILE); \
	      fi \
	   fi \
	fi
#
#       Install pcard extension.
	cd pcard/pcardext; \
	if [ "$(DESTDIR)" = "" ]; then \
	   $(PYTHON) setup.py install; \
	else \
	   $(PYTHON) setup.py install --root=$(DESTDIR) --prefix=$(prefix); \
	fi
#
#       Install cups extension.
	cd prnt/cupsext; \
	if [ "$(DESTDIR)" = "" ]; then \
	   $(PYTHON) setup.py install; \
	else \
	   $(PYTHON) setup.py install --root=$(DESTDIR) --prefix=$(prefix); \
	fi
##
#       Remove .py extensions in destdir and if not rpm_install create hp-xxx commands in bindir.
	for i in $(dist_cmd_SCRIPTS); do \
	    newname=$${i%.*}; \
	    mv $(DESTDIR)$(hplipdir)/$$i $(DESTDIR)$(hplipdir)/$$newname; \
	    if [ "$(rpm_install)" = "no" ]; then \
	      ln -sf ../share/$(PACKAGE)/$$newname $(DESTDIR)$(bindir)/hp-$$newname; \
	    fi \
	done
#
#       Edit hpiod.conf in destdir.
	echo -e "\n[$(PACKAGE)]\nversion=$(VERSION)\njdprobe=0\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	echo -e "[dirs]\nhome=$(hplipdir)\nrun=$(rundir)\nppd=$(hpppddir)\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	echo -ne "# Following values are determined at configure time and cannot be changed.\n[configure]\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	if [ "$(rpm_install)" = "yes" ]; then \
	   echo -ne "rpm-install=1\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -ne "rpm-install=0\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi 
	if [ "$(network_build)" = "yes" ]; then \
	   echo -ne "network-build=1\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -ne "network-build=0\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	if [ "$(pp_build)" = "yes" ]; then \
	   echo -ne "pp-build=1\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -ne "pp-build=0\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	echo -ne "internal-tag=$(PACKAGE_BUGREPORT)\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf;

#
#       Edit hpiod.sh in destdir.
	sed 's:HPIODDIR=:HPIODDIR=$(sbindir):' < $(DESTDIR)$(hplipdir)/$(PACKAGE).sh > $(DESTDIR)$(hplipdir)/$(PACKAGE).tmp; \
	sed 's:HPSSDDIR=:HPSSDDIR=$(hplipdir):' < $(DESTDIR)$(hplipdir)/$(PACKAGE).tmp > $(DESTDIR)$(hplipdir)/$(PACKAGE); \
	rm -f $(DESTDIR)$(hplipdir)/$(PACKAGE).tmp
#
#       Do full install if not rpm_install. Also only run chkconfig/install_initd if DESTDIR="". 
	if [ "$(rpm_install)" = "no" ]; then \
	   $(mkinstalldirs) $(DESTDIR)/etc/hp; \
	   $(INSTALL_DATA) $(DESTDIR)$(hplipdir)/$(PACKAGE).conf $(DESTDIR)/etc/hp; \
	   if [ -d $(DESTDIR)/etc/init.d ]; then \
	      $(INSTALL_SCRIPT) $(DESTDIR)$(hplipdir)/$(PACKAGE) $(DESTDIR)/etc/init.d; \
	      if [ "$(DESTDIR)" = "" ]; then \
	         if [ "$(INSTALLINITD)" != "" ]; then \
	            $(INSTALLINITD) $(PACKAGE); \
	         else \
	            $(CHKCONFIG) $(PACKAGE) reset; \
	         fi \
	      fi \
	   fi \
	fi
#
#       For internal testing.
	if [ "$(SHADOW)" != "" ]; then \
	   cp -f data/xml/unreleased/*.xml $(DESTDIR)$(hplipdir)/data/xml/; \
	fi
#
#       Install fax support. Let hpijs symlink hpppddir to cupsppddir.
	mv $(DESTDIR)$(hpfaxdir)/hpfax.py $(DESTDIR)$(hpfaxdir)/hpfax 
	if [ "$(rpm_install)" = "no" ]; then \
	   $(mkinstalldirs) $(DESTDIR)$(cupsdir); \
	   $(INSTALL_SCRIPT) $(DESTDIR)$(hpfaxdir)/hpfax $(DESTDIR)$(cupsdir); \
	   $(mkinstalldirs) $(DESTDIR)$(hpppddir)/fax; \
	   $(INSTALL_DATA) $(DESTDIR)$(faxppddir)/HP-Fax-hplip.ppd $(DESTDIR)$(hpppddir)/fax; \
	   gzip -f $(DESTDIR)$(hpppddir)/fax/HP-Fax-hplip.ppd; \
	fi

uninstall-hook:
#       Remove Icon file. 
	rm -f $(DESTDIR)$(icondir)/$(ICON_FILE)
	rm -f $(DESTDIR)$(ICON_PATH)/$(ICON_FILE)
#
#       Remove hp-xxx commands.
	for i in $(dist_cmd_SCRIPTS); do \
	    newname=$${i%.*}; \
	    rm -f $(DESTDIR)$(hplipdir)/$$newname; \
	    rm -f $(DESTDIR)$(bindir)/hp-$$newname; \
	done
#
#       Remove hplip.conf and hplip start/stop script.
	rm -f $(DESTDIR)/etc/hp/$(PACKAGE).conf
	rm -f $(DESTDIR)/etc/init.d/$(PACKAGE)
#
#       Remove fax support.
	rm -f $(DESTDIR)$(hpfaxdir)/hpfax 
	rm -f $(DESTDIR)$(cupsdir)/hpfax
	rm -f $(DESTDIR)$(hpppddir)/fax/HP-Fax-hplip.ppd.gz

#
# Add prerequisites for testing (or building?) "make install DESTDIR=/build".
test-destdir:
	if [ "$(DESTDIR)" != "" ]; then \
	   $(mkinstalldirs) $(DESTDIR)/etc/init.d; \
	   $(mkinstalldirs) $(DESTDIR)/etc/sane.d; \
	   if [ ! -f $(DESTDIR)/etc/sane.d/dll.conf ]; then \
	      touch $(DESTDIR)/etc/sane.d/dll.conf; \
	   fi; \
	   $(mkinstalldirs) $(DESTDIR)$(sanedir); \
	   $(mkinstalldirs) $(DESTDIR)/usr/share/applications; \
	   $(mkinstalldirs) $(DESTDIR)/usr/bin; \
	fi

dist-hook:
	if [ "$(SHADOW)" != "" ]; then \
	   cp -f data/xml/unreleased/*.xml $(distdir)/data/xml/; \
	fi

.PHONY: build-pcardext build-cupsext test-destdir

