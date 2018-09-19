TESTS = tests.py

check_SCRIPTS = tests.py

EXTRA_DIST = tests.py.in
CLEANFILES = $(check_SCRIPTS)

tests.py: tests.py.in
	$(AM_V_GEN) sed -e 's|@PYTHON[@]|$(PYTHON)|g' $< > $@
	chmod +x $@

# Default pep8.py --exclude + emacs backup files
PEP8_EXCLUDES=--exclude='.svn,CVS,.bzr,.hg,.git,__pycache__,.\#*'

check-local:
	pep8 --max-line-length=99 --ignore=E123,E402 $(PEP8_EXCLUDES) $(top_srcdir)/src/
