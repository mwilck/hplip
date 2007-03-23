#
#  Makefile.am - hplip automake input file
#
#  (c) 2004-2005 Copyright Hewlett-Packard Development Company, LP
#

SUBDIRS = . prnt/hpijs
INCLUDES = -Iip -Iapi

hplipdir = $(datadir)/hplip
rundir = /var/run

docdir = $(datadir)/doc/$(distdir)
doc_DATA = COPYING scan/sane/hpaio.desc

wwwsrc = doc

www0dir = $(docdir)
dist_www0_DATA = $(wwwsrc)/contacts.html $(wwwsrc)/faqs.html $(wwwsrc)/features.html $(wwwsrc)/index.html $(wwwsrc)/legal.html $(wwwsrc)/license.html $(wwwsrc)/mailing_lists.html \
   $(wwwsrc)/release_notes.html $(wwwsrc)/screenshots.html $(wwwsrc)/support_statement.html $(wwwsrc)/system_requirements.html $(wwwsrc)/about.html \
   $(wwwsrc)/other_support.html $(wwwsrc)/downloads.html
www1dir = $(docdir)/howtos
dist_www1_DATA = $(wwwsrc)/howtos/*
www2dir = $(docdir)/install
dist_www2_DATA = $(wwwsrc)/install/index.html
www21dir = $(docdir)/install/step1
dist_www21_DATA = $(wwwsrc)/install/step1/*
www22dir = $(docdir)/install/step2
dist_www22_DATA = $(wwwsrc)/install/step2/*
www23dir = $(docdir)/install/step3
dist_www23_DATA = $(wwwsrc)/install/step3/*
www24dir = $(docdir)/install/step4
dist_www24_DATA = $(wwwsrc)/install/step4/index.html
www241dir = $(docdir)/install/step4/cups
dist_www241_DATA = $(wwwsrc)/install/step4/cups/*
www242dir = $(docdir)/install/step4/setup
dist_www242_DATA = $(wwwsrc)/install/step4/setup/*
www243dir = $(docdir)/install/step4/suse
dist_www243_DATA = $(wwwsrc)/install/step4/suse/*
www251dir = $(docdir)/install/manual
dist_www251_DATA = $(wwwsrc)/install/manual/*
www252dir = $(docdir)/install/manual/distros
dist_www252_DATA = $(wwwsrc)/install/manual/distros/*
www261dir = $(docdir)/install/install
dist_www261_DATA = $(wwwsrc)/install/install/*
www3dir = $(docdir)/styles
dist_www3_DATA = $(wwwsrc)/styles/*
www4dir = $(docdir)/images
dist_www4_DATA = $(wwwsrc)/images/*
www5dir = $(docdir)/supported_devices
dist_www5_DATA = $(wwwsrc)/supported_devices/*
www6dir = $(docdir)/tech_docs
dist_www6_DATA = $(wwwsrc)/tech_docs/*
www61dir = $(docdir)/tech_docs/man_pages
dist_www61_DATA = $(wwwsrc)/tech_docs/man_pages/*
www7dir = $(docdir)/troubleshooting
dist_www7_DATA = $(wwwsrc)/troubleshooting/*

dist_hplip_DATA = $(doc_DATA) hplip.conf
dist_hplip_SCRIPTS = hpssd.py __init__.py hplip.sh install.py hplip-install

cmddir = $(hplipdir)
dist_cmd_SCRIPTS = align.py info.py print.py toolbox.py clean.py colorcal.py unload.py testpage.py makeuri.py check.py fab.py levels.py \
    sendfax.py setup.py makecopies.py probe.py timedate.py firmware.py

cupsdir = $(CUPS_BACKEND_PATH)
cupsppddir = $(CUPS_PPD_PATH)
ppddir = $(datadir)/ppd
hpppddir = $(datadir)/ppd/HP

# hp backend.
cups_PROGRAMS = hp
hp_SOURCES = backend/hp/hp.c 
hp_LDADD = libhplip-api.la

# hpiod
sbin_PROGRAMS = hpiod
hpiod_SOURCES = io/hpiod/hpiod.cpp io/hpiod/channel.cpp io/hpiod/device.cpp io/hpiod/mlc.cpp io/hpiod/system.cpp io/hpiod/jddevice.cpp io/hpiod/jetdirect.cpp \
    io/hpiod/udevice.cpp io/hpiod/uppdevice.cpp io/hpiod/ppdevice.cpp io/hpiod/pp.cpp io/hpiod/channel.h io/hpiod/device.h io/hpiod/hpiod.h io/hpiod/mlc.h \
    io/hpiod/system.h io/hpiod/dot4.cpp io/hpiod/ppdot4.cpp io/hpiod/dot4.h io/hpiod/usbext.c io/hpiod/usbext.h io/hpiod/comp.cpp

# base
basedir = $(hplipdir)/base
dist_base_SCRIPTS = base/maint.py base/codes.py base/g.py base/pml.py base/status.py  base/async.py \
    base/__init__.py base/mfpdtf.py base/utils.py base/async_qt.py base/kirbybase.py base/service.py \
    base/device.py base/logger.py base/msg.py base/slp.py base/exif.py base/strings.py base/magic.py \
    base/imagesize.py base/pexpect.py base/models.py base/mdns.py

# installer
installdir = $(hplipdir)/installer
installpagedir = $(hplipdir)/installer/pages
installscriptdir = $(hplipdir)/installer/scripts
installimagedir = $(hplipdir)/installer/images
installstyledir = $(hplipdir)/installer/styles
dist_install_SCRIPTS = installer/__init__.py installer/core.py installer/text_install.py installer/dcheck.py \
    installer/distros.py installer/web_install.py
dist_installpage_SCRIPTS = installer/pages/__init__.py installer/pages/install_required.tmpl installer/pages/installation_path.tmpl installer/pages/component.tmpl \
    installer/pages/mode.tmpl installer/pages/confirm_distro.tmpl installer/pages/notes.tmpl installer/pages/error.tmpl installer/pages/options.tmpl \
    installer/pages/error_package_manager.tmpl installer/pages/password.tmpl installer/pages/error_required_missing.tmpl installer/pages/progress.tmpl \
    installer/pages/error_unsupported_distro.tmpl installer/pages/ready_to_build.tmpl installer/pages/finished.tmpl installer/pages/select_distro.tmpl \
    installer/pages/hplip_remove.tmpl installer/pages/hpoj_remove.tmpl installer/pages/turn_off_options.tmpl \
    installer/pages/index.tmpl installer/pages/welcome.tmpl installer/pages/install_optional.tmpl installer/pages/quit.tmpl
dist_installscript_SCRIPTS = installer/scripts/hplip.js installer/scripts/xml_loader.js
dist_installimage_DATA = installer/images/button.png installer/images/favicon.ico installer/images/topbar.png installer/images/view.png \
    installer/images/back.png installer/images/circular.gif installer/images/hplogo.png installer/images/tux.png \
    installer/images/button1.png  installer/images/button1d.png
dist_installstyle_SCRIPTS = installer/styles/hplip.css

# makecopies
copierdir = $(hplipdir)/copier
dist_copier_SCRIPTS = copier/copier.py copier/__init__.py

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
modelsdir = $(hplipdir)/data/models
imagesdir = $(hplipdir)/data/images
pcldir = $(hplipdir)/data/pcl
ldldir = $(hplipdir)/data/ldl
psdir = $(hplipdir)/data/ps
firmdir = $(hplipdir)/data/firmware
icondir = $(hplipdir)/data
dist_ps_DATA = data/ps/testpage.ps.gz data/ps/clean_page.pdf.gz
dist_models_DATA = data/models/models.dat
dist_images_DATA = data/images/*
dist_pcl_DATA = data/pcl/align1_8xx.pcl.gz data/pcl/align1_9xx.pcl.gz data/pcl/align2_8xx.pcl.gz data/pcl/align3_8xx.pcl.gz data/pcl/align4_8xx.pcl.gz \
    data/pcl/align5_8xx.pcl.gz data/pcl/align2_9xx.pcl.gz data/pcl/align3_9xx.pcl.gz data/pcl/align4_450.pcl.gz data/pcl/align6_450.pcl.gz \
    data/pcl/colorcal1_450.pcl.gz data/pcl/colorcal2_450.pcl.gz data/pcl/crbcal.pcl.gz data/pcl/crcaldone.pcl.gz data/pcl/crcbcal.pcl.gz data/pcl/crccal.pcl.gz \
    data/pcl/crcpcal.pcl.gz data/pcl/crpcal.pcl.gz 
dist_ldl_DATA = data/ldl/cb2pcal.ldl.gz data/ldl/cb2pcal_done.ldl.gz data/ldl/cbbcal.ldl.gz data/ldl/cbccal.ldl.gz data/ldl/cbccal_done.ldl.gz data/ldl/cbcpcal.ldl.gz \
    data/ldl/cbpcal.ldl.gz
dist_firm_DATA = data/firmware/HP_LaserJet_1018.fw.gz data/firmware/HP_LaserJet_1020.fw.gz

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
dist_prnt_SCRIPTS = prnt/cups.py prnt/__init__.py prnt/ldl.py prnt/pcl.py prnt/colorcal.py prnt/printable_areas.py

# scan
scandir = $(hplipdir)/scan
dist_scan_SCRIPTS = scan/__init__.py

if SCAN_BUILD
lib_LTLIBRARIES = libhpip.la libsane-hpaio.la
else
lib_LTLIBRARIES = libhpip.la
endif

# ip library
libhpip_la_SOURCES = ip/xconvolve.c ip/xfax.c ip/xgrayout.c ip/xjpg_dct.c ip/xjpg_fix.c ip/xpad.c ip/xrotate.c ip/xskel.c ip/xtiff.c \
    ip/ipmain.c ip/xchgbpp.c ip/xcrop.c ip/xgamma.c ip/xjpg_dec.c ip/xjpg_huf.c ip/xpcx.c ip/xsaturation.c ip/xtable.c ip/xtonemap.c \
    ip/xbi2gray.c ip/xcolrspc.c ip/xfakemono.c ip/xgray2bi.c ip/xinvert.c ip/xjpg_enc.c ip/xmatrix.c ip/xpnm.c ip/xscale.c ip/xthumb.c ip/xyxtract.c \
    ip/hpip.h ip/ipdefs.h ip/xform.h ip/xjpg_dct.h ip/xjpg_huf.h ip/xjpg_mrk.h 
libhpip_la_LDFLAGS = -version-info 0:1:0

if SCAN_BUILD

# hpaio sane backend
MAJORVER=1
MINORVER=0
AGEVER=0
BASENAME=sane-hpaio
SONOVER=lib$(BASENAME).so
SOSHORT=$(SONOVER).$(MAJORVER)
SOLONG=$(SOSHORT).$(MINORVER).$(AGEVER)
sanedir = $(libdir)/sane
#lib_LTLIBRARIES = libsane-hpaio.la
libsane_hpaio_la_SOURCES = scan/sane/hpaio.c scan/sane/mfpdtf.c scan/sane/pml.c scan/sane/scl.c scan/sane/io.c scan/sane/hpaio.h \
      scan/sane/pml.h scan/sane/saneopts.h scan/sane/io.h scan/sane/mfpdtf.h scan/sane/sane.h scan/sane/scl.h scan/sane/tables.h \
      scan/sane/common.c scan/sane/common.h scan/sane/soap.h scan/sane/sanei_debug.h scan/sane/sanei.h \
      scan/sane/soap_stub.c scan/sane/sanei_init_debug.c
#      scan/sane/soap.c scan/sane/webScanC.c scan/sane/webScanClient.c scan/sane/stdsoap2.c \
#      scan/sane/dime.c scan/sane/dime.h scan/sane/webScanStub.h scan/sane/webScanH.h scan/sane/stdsoap2.h scan/sane/webScan.nsmap
libsane_hpaio_la_LDFLAGS = -version-info $(MAJORVER):$(MINORVER):$(AGEVER) 
# The following is a interlibrary dependency that must be compiled first.
libsane_hpaio_la_LIBADD = libhpip.la libhplip-api.la
#libsane_hpaio_la_CFLAGS = -DWITH_NONAMESPACES -DSOAP_DEBUG
libsane_hpaio_la_CFLAGS = -DWITH_NONAMESPACES -DWITH_LEAN

endif

# api library
noinst_LTLIBRARIES = libhplip-api.la
libhplip_api_la_SOURCES = api/hplip_api.c api/hplip_api.h api/model.c api/list.h

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
    ui/faxsendjobform_base.py ui/faxsendjobform.py ui/faxsettingsform_base.py ui/faxsettingsform.py \
    ui/coverpageform_base.py ui/coverpageform.py ui/allowabletypesdlg_base.py ui/allowabletypesdlg.py \
    ui/makecopiesform_base.py ui/makecopiesform.py ui/setupform_base.py ui/setupform.py ui/setupmanualfind_base.py \
    ui/setupmanualfind.py ui/setupsettings_base.py ui/setupsettings.py ui/scrollview.py ui/scrollfunc.py ui/scrollstatus.py \
    ui/scrollprintsettings.py ui/scrollprintcontrol.py ui/scrolltool.py ui/scrollsupplies.py  ui/scrollprint.py ui/scrollfax.py

dist_noinst_DATA = ui/unloadform_base.ui ui/colorcalform2_base.ui ui/settingsdialog_base.ui ui/aligntype6form1_base.ui \
    ui/aboutdlg_base.ui ui/imagepropertiesdlg_base.ui ui/paperedgealignform_base.ui ui/aligntype6form2_base.ui \
    ui/nodevicesform_base.ui ui/cleaningform_base.ui ui/colorcalform_base.ui ui/devmgr4_base.ui ui/loadpaperform_base.ui \
    ui/cleaningform2_base.ui ui/waitform_base.ui ui/coloradjform_base.ui ui/faxaddrbookeditform_base.ui \
    ui/faxaddrbookform_base.ui ui/faxaddrbookgroupeditform_base.ui ui/faxaddrbookgroupsform_base.ui \
    ui/align10form_base.ui  \
    plugins/powersettingsdialog_base.ui ui/faxsendjobform_base.ui ui/faxsettingsform_base.ui ui/coverpageform_base.ui \
    ui/allowabletypesdlg_base.ui ui/makecopiesform_base.ui ui/setupform_base.ui ui/setupmanualfind_base.ui \
    ui/setupsettings_base.ui

# ui plugins
pluginsdir = $(hplipdir)/plugins
dist_plugins_SCRIPTS = plugins/dj450.py plugins/__init__.py plugins/powersettings.py plugins/powersettingsdialog.py \
    plugins/powersettingsdialog_base.py plugins/Deskjet_460.py

# cheetah
cheetahdir = $(hplipdir)/Cheetah
cheetahutildir = $(hplipdir)/Cheetah/Utils
cheetahoptikdir = $(hplipdir)/Cheetah/Utils/optik
dist_cheetah_SCRIPTS = Cheetah/Filters.py Cheetah/SettingsManager.py Cheetah/CheetahWrapper.py Cheetah/ImportHooks.py \
    Cheetah/SourceReader.py Cheetah/Compiler.py Cheetah/ImportManager.py Cheetah/Template.py Cheetah/DummyTransaction.py \
    Cheetah/NameMapper.py Cheetah/TemplateCmdLineIface.py Cheetah/ErrorCatchers.py Cheetah/Parser.py Cheetah/Version.py \
    Cheetah/FileUtils.py Cheetah/Servlet.py Cheetah/CacheRegion.py Cheetah/__init__.py
dist_cheetahutil_SCRIPTS = Cheetah/Utils/Indenter.py Cheetah/Utils/Misc.py Cheetah/Utils/VerifyType.py \
    Cheetah/Utils/WebInputMixin.py Cheetah/Utils/__init__.py
dist_cheetahoptik_SCRIPTS = Cheetah/Utils/optik/errors.py Cheetah/Utils/optik/option_parser.py Cheetah/Utils/optik/option.py \
    Cheetah/Utils/optik/__init__.py

# cherrypy
cherrydir = $(hplipdir)/cherrypy
cherrylibdir = $(hplipdir)/cherrypy/lib
cherryfiltersdir = $(hplipdir)/cherrypy/filters
dist_cherry_SCRIPTS = cherrypy/_cphttptools.py cherrypy/_cpwsgi.py cherrypy/__init__.py cherrypy/_cpserver.py cherrypy/_cpwsgiserver.py \
    cherrypy/_cpcgifs.py cherrypy/_cpthreadinglocal.py cherrypy/config.py cherrypy/_cpengine.py cherrypy/_cptree.py cherrypy/_cperror.py \
    cherrypy/_cputil.py 
dist_cherrylib_SCRIPTS = cherrypy/lib/covercp.py cherrypy/lib/form.py cherrypy/lib/__init__.py cherrypy/lib/cptools.py \
    cherrypy/lib/httptools.py cherrypy/lib/autoreload.py cherrypy/lib/defaultformmask.py cherrypy/lib/profiler.py
dist_cherryfilters_SCRIPTS = cherrypy/filters/nsgmlsfilter.py cherrypy/filters/__init__.py \
    cherrypy/filters/responseheadersfilter.py \
    cherrypy/filters/basefilter.py cherrypy/filters/sessionauthenticatefilter.py cherrypy/filters/baseurlfilter.py \
    cherrypy/filters/sessionfilter.py cherrypy/filters/cachefilter.py cherrypy/filters/staticfilter.py \
    cherrypy/filters/decodingfilter.py cherrypy/filters/tidyfilter.py cherrypy/filters/encodingfilter.py \
    cherrypy/filters/virtualhostfilter.py cherrypy/filters/gzipfilter.py cherrypy/filters/wsgiappfilter.py \
    cherrypy/filters/logdebuginfofilter.py cherrypy/filters/xmlrpcfilter.py

build-pcardext: 
	cd pcard/pcardext; \
	$(PYTHON) setup.py build

build-cupsext: 
	cd prnt/cupsext; \
	$(PYTHON) setup.py build

install-pcardext:
	cd pcard/pcardext; \
	if [ "$(DESTDIR)" = "" ]; then \
	   $(PYTHON) setup.py install --prefix=$(prefix); \
	else \
	   $(PYTHON) setup.py install --root=$(DESTDIR) --prefix=$(prefix); \
	fi

install-cupsext:
	cd prnt/cupsext; \
	if [ "$(DESTDIR)" = "" ]; then \
	   $(PYTHON) setup.py install --prefix=$(prefix); \
	else \
	   $(PYTHON) setup.py install --root=$(DESTDIR) --prefix=$(prefix); \
	fi

install-exec-hook:
#
#       If scanner build, install sane backend.
	if [ "$(scan_build)" = "yes" ]; then \
	   $(mkinstalldirs) $(DESTDIR)/etc/sane.d; \
	   if [ ! -f $(DESTDIR)/etc/sane.d/dll.conf ]; then \
	      touch $(DESTDIR)/etc/sane.d/dll.conf; \
	   fi; \
	   $(mkinstalldirs) $(DESTDIR)$(sanedir); \
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

install-data-hook: install-pcardext install-cupsext
#
#       Create ICON file in srcdir.
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
#       Install ICON file in destdir.
	if [ "$(ICON_FILE)" != "" ]; then \
	   $(mkinstalldirs) $(DESTDIR)$(ICON_PATH); \
	   ln -sf $(icondir)/$(ICON_FILE) $(DESTDIR)$(ICON_PATH)/$(ICON_FILE); \
	fi 
#
#       Remove .py extensions in destdir and create hp-xxx commands in bindir.
	$(mkinstalldirs) $(DESTDIR)$(bindir)
	for i in $(dist_cmd_SCRIPTS); do \
	   newname=$${i%.*}; \
	   mv $(DESTDIR)$(hplipdir)/$$i $(DESTDIR)$(hplipdir)/$$newname; \
	   if [ ! \( "$$newname" = "toolbox" -a "$(gui_build)" = "no" \) ]; then \
	      ln -sf ../share/$(PACKAGE)/$$newname $(DESTDIR)$(bindir)/hp-$$newname; \
	   fi \
	done
#
#       Edit hpiod.conf in destdir.
	echo -e "\n[$(PACKAGE)]\nversion=$(VERSION)\njdprobe=0\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	echo -e "[dirs]\nhome=$(hplipdir)\nrun=$(rundir)\nppd=$(hpppddir)\nppdbase=$(ppddir)\ndoc=$(docdir)\n" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	echo -e "# Following values are determined at configure time and cannot be changed.\n[configure]" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	if [ "$(network_build)" = "yes" ]; then \
	   echo -e "network-build=1" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -e "network-build=0" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	if [ "$(pp_build)" = "yes" ]; then \
	   echo -e "pp-build=1" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -e "pp-build=0" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	if [ "$(gui_build)" = "yes" ]; then \
	   echo -e "gui-build=1" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -e "gui-build=0" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	if [ "$(scan_build)" = "yes" ]; then \
	   echo -e "scanner-build=1" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -e "scanner-build=0" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	if [ "$(fax_build)" = "yes" ]; then \
	   echo -e "fax-build=1" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -e "fax-build=0" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	if [ "$(cups11_build)" = "yes" ]; then \
	   echo -e "cups11-build=1" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	else \
	   echo -e "cups11-build=0" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf; \
	fi
	echo -e "installinitd=$(INSTALLINITD)\nchkconfig=$(CHKCONFIG)" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
	echo -e "internal-tag=$(PACKAGE_BUGREPORT)" >> $(DESTDIR)$(hplipdir)/$(PACKAGE).conf
#
#       Install hpiod.conf. 
	$(mkinstalldirs) $(DESTDIR)/etc/hp
	$(INSTALL_DATA) $(DESTDIR)$(hplipdir)/$(PACKAGE).conf $(DESTDIR)/etc/hp
#
#       Create hpiod start/stop script from hpiod.sh in destdir.
	sed 's:HPIODDIR=:HPIODDIR=$(sbindir):' < $(DESTDIR)$(hplipdir)/$(PACKAGE).sh > $(DESTDIR)$(hplipdir)/$(PACKAGE).tmp; \
	sed 's:HPSSDDIR=:HPSSDDIR=$(hplipdir):' < $(DESTDIR)$(hplipdir)/$(PACKAGE).tmp > $(DESTDIR)$(hplipdir)/$(PACKAGE); \
	rm -f $(DESTDIR)$(hplipdir)/$(PACKAGE).tmp
#
#       Install hpiod start/stop script.
	$(mkinstalldirs) $(DESTDIR)/etc/init.d
	$(INSTALL_SCRIPT) $(DESTDIR)$(hplipdir)/$(PACKAGE) $(DESTDIR)/etc/init.d
#
#       Run chkconfig/install_initd if DESTDIR="". 
	if [ "$(DESTDIR)" = "" ]; then \
	   if [ "$(INSTALLINITD)" != "" ]; then \
	      $(INSTALLINITD) $(PACKAGE); \
	   elif [ "$(CHKCONFIG)" != "" ]; then  \
	      $(CHKCONFIG) $(PACKAGE) reset; \
	   fi \
	fi
#
#       Install fax support. Let hpijs symlink hpppddir to cupsppddir.
	if [ "$(fax_build)" = "yes" ]; then \
	   mv $(DESTDIR)$(hpfaxdir)/hpfax.py $(DESTDIR)$(hpfaxdir)/hpfax; \
	   $(mkinstalldirs) $(DESTDIR)$(cupsdir); \
	   $(INSTALL_SCRIPT) $(DESTDIR)$(hpfaxdir)/hpfax $(DESTDIR)$(cupsdir); \
	   $(mkinstalldirs) $(DESTDIR)$(hpppddir)/fax; \
	   $(INSTALL_DATA) $(DESTDIR)$(faxppddir)/HP-Fax-hplip.ppd $(DESTDIR)$(hpppddir)/fax; \
	   gzip -f $(DESTDIR)$(hpppddir)/fax/HP-Fax-hplip.ppd; \
	fi
#
#       For internal testing.
	if [ "$(SHADOW)" != "" ]; then \
	$(mkinstalldirs) $(DESTDIR)$(modelsdir)/unreleased; \
	$(INSTALL_DATA) $(srcdir)/data/models/unreleased.dat $(DESTDIR)$(modelsdir)/unreleased; \
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

dist-hook:
	if [ "$(SHADOW)" != "" ]; then \
	   cp -f data/models/unreleased/unreleased.dat $(distdir)/data/models/; \
	fi

.PHONY: build-pcardext build-cupsext install-pcardext install-cupsext

