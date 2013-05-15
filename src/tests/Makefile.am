TESTS = tests.py

check_SCRIPTS = tests.py

EXTRA_DIST = tests.py


# Default pep8.py --exclude + emacs backup files
PEP8_EXCLUDES=--exclude='.svn,CVS,.bzr,.hg,.git,__pycache__,.\#*'

check-local:
	pep8 --max-line-length=99 --ignore=E123 $(PEP8_EXCLUDES) $(top_srcdir)/src/
