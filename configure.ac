AC_PREREQ([2.64])
AC_INIT([d-feet],
	[0.3.4],
	[http://bugzilla.gnome.org/enter_bug.cgi?product=d-feet],
        [d-feet],
        [http://live.gnome.org/DFeet])

AM_INIT_AUTOMAKE([1.11 -Wall foreign no-define tar-ustar no-dist-gzip dist-xz])

GLIB_GSETTINGS

PKG_PROG_PKG_CONFIG

GNOME_COMPILE_WARNINGS([maximum])

YELP_HELP_INIT

AM_PATH_PYTHON([2.7])

PKG_CHECK_MODULES(DFEET, [
  gtk+-3.0 >= 3.6
])

AC_CHECK_PROG([PEP8], [pep8], [yes])
test -z "$PEP8" && AC_MSG_ERROR([pep8 binary not found but needed for testsuite])

# i18n stuff
IT_PROG_INTLTOOL([0.40.0])

AM_GNU_GETTEXT_VERSION([0.17])
AM_GNU_GETTEXT([external])

GETTEXT_PACKAGE=AC_PACKAGE_NAME
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [Package name for gettext])

AC_CONFIG_FILES([
	Makefile
	po/Makefile.in
	src/Makefile
	src/dfeet/Makefile
	src/tests/Makefile
	data/Makefile
	data/d-feet.desktop.in
	data/icons/Makefile
	data/ui/Makefile
	help/Makefile
])

AC_OUTPUT
