SUBDIRS = icons ui

gsettings_SCHEMAS = org.gnome.d-feet.gschema.xml
@GSETTINGS_RULES@

@INTLTOOL_DESKTOP_RULE@

desktopdir = $(datadir)/applications
desktop_in_files = d-feet.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

UPDATE_DESKTOP = update-desktop-database $(datadir)/applications || :

install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)

EXTRA_DIST =			\
	$(desktop_in_files)	\
	$(gsettings_SCHEMAS)

CLEANFILES =			\
	$(DESKTOP_FILES)

DISTCLEANFILES =		\
	$(desktop_DATA)
