SUBDIRS = icons ui

gsettings_SCHEMAS = org.gnome.d-feet.gschema.xml
@GSETTINGS_RULES@

@INTLTOOL_DESKTOP_RULE@

desktopdir = $(datadir)/applications
desktop_in_files = d-feet.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

UPDATE_DESKTOP = if test -z "$(DESTDIR)"; then update-desktop-database $(datadir)/applications || :; fi

@INTLTOOL_XML_RULE@
appdatadir = $(datadir)/appdata
appdata_DATA = $(appdata_in_files:.xml.in=.xml)
appdata_in_files = d-feet.appdata.xml.in


install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)

EXTRA_DIST =			\
	$(desktop_in_files)	\
	$(gsettings_SCHEMAS)	\
	$(appdata_DATA)

CLEANFILES =			\
	$(DESKTOP_FILES)	\
	$(appdata_DATA)

DISTCLEANFILES =		\
	$(desktop_DATA)
