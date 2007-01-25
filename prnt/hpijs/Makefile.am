if HPLIP_BUILD
INCLUDES = -I../../ip -I../../api
endif

docdir	= $(datadir)/doc/$(distdir)
ppddir = $(datadir)/ppd/HP

#APDKLABEL=JetReady_PreMerge_11-08-04 
APDKLABEL=APDK_2007_01_11
APDKCOMMON=slimhost/source/common
APDKOPEN=slimhost/source/open
APDKDEBUG=slimhost/source/debug

#FOOMATICLABEL=foomatic-3_0-branch
FOOMATICLABEL=

#BZRSERVER=http://bzr.linuxprinting.org/devel
BZRSERVER=http://dsufflnx/bzr

if FOOMATIC_INSTALL
foomatichook = install-foomatic
unfoomatichook = uninstall-foomatic
rip = foomatic-rip
if CUPS_INSTALL
cupshook = install-cups
uncupshook = uninstall-cups
else
cupshook =
uncupshook =
endif
else
foomatichook =
unfoomatichook = 
rip =
cupshook =
uncupshook =
endif

bin_PROGRAMS = hpijs
apdk_SOURCES = models.cpp breaks_open.cpp \
	dj9xxvip.cpp dj9xx.cpp capture.cpp colormatch.cpp colormatcher_open.cpp \
	compression.cpp context.cpp create_so.cpp creator.cpp \
	dj600.cpp dj630.cpp dj660.cpp dj690.cpp dj6xx.cpp dj8xx.cpp dj600_maps.cpp \
	dj660_maps.cpp dj690_maps.cpp dj895_maps.cpp dj895_maps2.cpp dj970_maps.cpp \
	dj970_maps2.cpp dj970_maps3.cpp filterhpa.cpp apollo21xx.cpp apollo2560.cpp apollo2xxx.cpp \
	dj8x5.cpp psp100.cpp phobos_cmaps.cpp dj350.cpp halftoner.cpp halftoner_open.cpp \
	globals.cpp header.cpp htmtxhi.cpp pmselect.cpp \
	job.cpp printer.cpp registry.cpp scaler.cpp \
	scaler_open.cpp script.cpp systemservices.cpp \
	translator.cpp version.cpp versioncode.cpp \
	djgenericvip.cpp dj540.cpp dj850.cpp dj850_maps.cpp dj890.cpp \
	apollo21xx.h apollo2560.h apollo2xxx.h colormatch.h colormatcher_open.h \
	compression.h config.h context.h dj350.h dj400.h dj540.h \
	dj600.h dj630.h dj660.h dj690.h dj6xx.h dj8x5.h dj8xx.h dj850.h dj890.h dj9xx.h dj9xxvip.h \
	ernieplatform.h filterhpa.h global_types.h halftoner.h font.h debug.h \
	halftoner_open.h header.h hpprint_c_api.h \
	hpprintapi.h hptypes.h htfed.h internal.h \
	interp.h interp_data_50.h io_defs.h job.h models.h modes.h pmselect.h \
	printer.h psp100.h psp470.h resources.h scaler_open.h scaler_prop.h script.h \
	systemservices.h unistd_.h djgenericvip.h ljmono.h ljmono.cpp \
	dj3320.cpp dj3320.h dj3320_cmap.cpp dj3600.cpp dj3600.h dj3600_cmap.cpp dj4100.h \
	dj4100_cmap.cpp ldlencap.h ljcolor.cpp ljcolor.h pscript.h \
	printerproxy.cpp printerfactory.cpp printerproxy.h printerfactory.h \
	ljjetready.cpp ljjetready.h jdatadbf.c jccolor.c ljfastraster.cpp ljfastraster.h \
	jinclude.h jpegint.h dj55xx.h hpijsfax.h ojprokx50.h 
                
hpijs_SOURCES = $(apdk_SOURCES) hpijs.cpp ijs_server.c ijs.c hpijsfax.cpp services.cpp \
    hpijs.h ijs.h ijs_server.h services.h ijs_client.h hpiom.c hpiom.h 

noinst_PROGRAMS = hppgsz
hppgsz_SOURCES = $(apdk_SOURCES) PrinterProperties.cpp PrinterProperties.h

if HPLIP_BUILD
hpijs_LDADD = ../../libhpip.la ../../libhplip-api.la
endif

doc_DATA = COPYING README_LIBJPG
bin_SCRIPTS = $(rip)

wwwsrc = ../../doc

# HPLIP and HPIJS documention are the same, only install one copy if HPLIP build.
if !HPLIP_BUILD
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
endif

EXTRA_DIST = $(doc_DATA) ppd foomatic-rip hpijs-ppd gdevijs-krgb-1.3-gs8.54.patch

install-data-hook: $(foomatichook) $(cupshook)
uninstall-hook: $(unfoomatichook) $(uncupshook)

install-foomatic:
	$(mkinstalldirs) $(DESTDIR)$(ppddir)
	rm -f $(DESTDIR)$(ppddir)/HP*.ppd*
	rm -f $(DESTDIR)$(ppddir)/hp*.ppd*
	$(INSTALL_DATA) ppd/* $(DESTDIR)$(ppddir)
	gzip -f $(DESTDIR)$(ppddir)/HP*
	gzip -f $(DESTDIR)$(ppddir)/hp*

uninstall-foomatic:
	rm -f $(DESTDIR)$(ppddir)/HP*.ppd*
	rm -f $(DESTDIR)$(ppddir)/hp*.ppd*

install-cups:
	rm -f $(DESTDIR)$(CUPS_PPD_PATH)/HP*.ppd* $(DESTDIR)$(CUPS_PPD_PATH)/foomatic/HP/HP*.ppd*
	rm -f $(DESTDIR)$(CUPS_PPD_PATH)/hp*.ppd* $(DESTDIR)$(CUPS_PPD_PATH)/foomatic/HP/hp*.ppd*
	rm -f $(DESTDIR)$(CUPS_PPD_PATH)/foomatic-ppds
	$(mkinstalldirs) $(DESTDIR)$(CUPS_PPD_PATH)
	ln -s $(datadir)/ppd $(DESTDIR)$(CUPS_PPD_PATH)/foomatic-ppds
	rm -f $(DESTDIR)$(CUPS_FILTER_PATH)/foomatic-rip
	$(mkinstalldirs) $(DESTDIR)$(CUPS_FILTER_PATH)
	ln -s $(bindir)/foomatic-rip $(DESTDIR)$(CUPS_FILTER_PATH)/foomatic-rip

uninstall-cups:
	rm -f $(DESTDIR)$(CUPS_PPD_PATH)/foomatic-ppds
	rm -f $(DESTDIR)$(CUPS_FILTER_PATH)/foomatic-rip

get-apdk: 
	cvs -z3 -d:pserver:$(USER)@elkhorn1.vcd.hp.com:/shared/data/ccvs/repository co -r $(APDKLABEL) $(APDKCOMMON)
	cvs -z3 -d:pserver:$(USER)@elkhorn1.vcd.hp.com:/shared/data/ccvs/repository co -r $(APDKLABEL) $(APDKOPEN)
	cvs -z3 -d:pserver:$(USER)@elkhorn1.vcd.hp.com:/shared/data/ccvs/repository co -r $(APDKLABEL) $(APDKDEBUG)
	cp -f $(APDKCOMMON)/*.cpp $(APDKCOMMON)/*.h $(APDKCOMMON)/*.c $(APDKCOMMON)/README_LIBJPG ./
	cp -f $(APDKOPEN)/*.cpp $(APDKOPEN)/*.h ./
	cp -f $(APDKDEBUG)/*.cpp $(APDKDEBUG)/*.h ./
	rm -rf slimhost

get-apdk-tip: 
	cvs -z3 -d:pserver:$(USER)@elkhorn1.vcd.hp.com:/shared/data/ccvs/repository co $(APDKCOMMON)
	cvs -z3 -d:pserver:$(USER)@elkhorn1.vcd.hp.com:/shared/data/ccvs/repository co $(APDKOPEN)
	cvs -z3 -d:pserver:$(USER)@elkhorn1.vcd.hp.com:/shared/data/ccvs/repository co $(APDKDEBUG)
	cp -f $(APDKCOMMON)/*.cpp $(APDKCOMMON)/*.h $(APDKCOMMON)/*.c $(APDKCOMMON)/README_LIBJPG ./
	cp -f $(APDKOPEN)/*.cpp $(APDKOPEN)/*.h ./
	cp -f $(APDKDEBUG)/*.cpp $(APDKDEBUG)/*.h ./
	rm -rf slimhost

get-ppd: 
	rm -rf foomatic-db-engine
	rm -rf foomatic-filters
	rm -rf foomatic-db
	rm -rf foomatic-db-hpijs
	bzr branch $(BZRSERVER)/foomatic-db-engine
	bzr branch $(BZRSERVER)/foomatic-filters 
	bzr branch $(BZRSERVER)/foomatic-db
	bzr branch $(BZRSERVER)/foomatic-db-hpijs
	cd foomatic-db-hpijs; \
	./make_configure; \
	./configure; \
	make inplace
	cd foomatic-filters; \
	./make_configure; \
	./configure; \
	make inplace
	cd foomatic-db-engine; \
	./make_configure; \
	./configure; \
	make inplace
	./hpijs-ppd
	cp foomatic-filters/foomatic-rip ./
	cp foomatic-db/db/source/PPD/HP/all_in_one/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/business_inkjet/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/color_laser/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/mono_laser/*.ppd ppd/
	rm -rf foomatic-db-engine
	rm -rf foomatic-filters
	rm -rf foomatic-db
	rm -rf foomatic-db-hpijs
	sed -e 's/DefaultInputSlot: Default/DefaultInputSlot: Upper/' < ppd/HP-PhotoSmart_8700-hpijs.ppd > ppd/ppd.tmp
	rm ppd/HP-PhotoSmart_8700-hpijs.ppd
	mv ppd/ppd.tmp ppd/HP-PhotoSmart_8700-hpijs.ppd

get-ppd-shadow:
	rm -rf foomatic-db-engine
	rm -rf foomatic-filters
	rm -rf foomatic-db
	rm -rf foomatic-db-hpijs
	bzr branch $(BZRSERVER)/foomatic-db-engine
	bzr branch $(BZRSERVER)/foomatic-filters
	bzr branch $(BZRSERVER)/foomatic-db
	bzr branch $(BZRSERVER)/foomatic-db-hpijs
	-cp -f foomatic/foomatic-db/*.xml foomatic-db/db/source/printer/
	-cp -f foomatic/foomatic-db-hpijs/hpijs-generator.in foomatic-db-hpijs/data-generators/hpijs/
	-cp -f foomatic/foomatic-db-hpijs/hpijs-printermap foomatic-db-hpijs/data-generators/hpijs/
	cd foomatic-db-hpijs; \
	./make_configure; \
	./configure; \
	make inplace
	cd foomatic-filters; \
	./make_configure; \
	./configure; \
	make inplace
	cd foomatic-db-engine; \
	./make_configure; \
	./configure; \
	make inplace
	./hpijs-ppd
	cp foomatic-filters/foomatic-rip ./
	cp foomatic-db/db/source/PPD/HP/all_in_one/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/business_inkjet/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/color_laser/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/mono_laser/*.ppd ppd/
	-cp -f foomatic/foomatic-db/db/source/PPD/HP/all_in_one/*.ppd ppd/
	-cp -f foomatic/foomatic-db/db/source/PPD/HP/business_inkjet/*.ppd ppd/
	-cp -f foomatic/foomatic-db/db/source/PPD/HP/color_laser/*.ppd ppd/
	-cp -f foomatic/foomatic-db/db/source/PPD/HP/mono_laser/*.ppd ppd/
	rm -rf foomatic-db-engine
	rm -rf foomatic-filters
	rm -rf foomatic-db
	rm -rf foomatic-db-hpijs
	sed -e 's/DefaultInputSlot: Default/DefaultInputSlot: Upper/' < ppd/HP-PhotoSmart_8700-hpijs.ppd > ppd/ppd.tmp
	rm ppd/HP-PhotoSmart_8700-hpijs.ppd
	mv ppd/ppd.tmp ppd/HP-PhotoSmart_8700-hpijs.ppd

get-foomatic:
	bzr branch $(BZRSERVER)/foomatic-db-engine
	bzr branch $(BZRSERVER)/foomatic-filters
	bzr branch $(BZRSERVER)/foomatic-db
	bzr branch $(BZRSERVER)/foomatic-db-hpijs

test-ppd:
	cd foomatic-db-hpijs; \
	./make_configure; \
	./configure; \
	make inplace
	cd foomatic-filters; \
	./make_configure; \
	./configure; \
	make inplace
	cd foomatic-db-engine; \
	./make_configure; \
	./configure; \
	make inplace
	./hpijs-ppd
	cp foomatic-filters/foomatic-rip ./
	cp foomatic-db/db/source/PPD/HP/all_in_one/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/business_inkjet/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/color_laser/*.ppd ppd/
	cp foomatic-db/db/source/PPD/HP/mono_laser/*.ppd ppd/

test-clean:
	cd foomatic-db-hpijs; \
	make clean
	cd foomatic-filters; \
	make clean
	cd foomatic-db-engine; \
	make clean


