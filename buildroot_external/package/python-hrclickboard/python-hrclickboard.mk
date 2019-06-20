################################################################################
#
# python-hrclickboard
#
################################################################################

PYTHON_HRCLICKBOARD_VERSION = 1.0
PYTHON_HRCLICKBOARD_SITE = $(BR2_EXTERNAL_HRWILC_PATH)/package/python-hrclickboard
PYTHON_HRCLICKBOARD_SOURCE = HRClickBoard.tar.xz
PYTHON_HRCLICKBOARD_SITE_METHOD = file
PYTHON_HRCLICKBOARD_SETUP_TYPE = setuptools

$(eval $(python-package))
