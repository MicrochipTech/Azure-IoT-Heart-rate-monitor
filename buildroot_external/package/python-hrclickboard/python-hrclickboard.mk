################################################################################
#
# python-hrclickboard
#
################################################################################

PYTHON_HRCLICKBOARD_VERSION = 1.0
PYTHON_HRCLICKBOARD_SITE = $(BR2_EXTERNAL_HRWILC_PATH)/package/python-hrclickboard/HRClickBoard
PYTHON_HRCLICKBOARD_SITE_METHOD = local
PYTHON_HRCLICKBOARD_SETUP_TYPE = setuptools

$(eval $(python-package))
