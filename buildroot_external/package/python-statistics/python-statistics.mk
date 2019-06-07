################################################################################
#
# python-statistics
#
################################################################################

PYTHON_STATISTICS_VERSION = 1.0.3.5
PYTHON_STATISTICS_SOURCE = statistics-$(PYTHON_STATISTICS_VERSION).tar.gz
PYTHON_STATISTICS_SITE = https://files.pythonhosted.org/packages/bb/3a/ae99a15e65636559d936dd2159d75af1619491e8cb770859fbc8aa62cef6
PYTHON_STATISTICS_SETUP_TYPE = setuptools

$(eval $(python-package))
