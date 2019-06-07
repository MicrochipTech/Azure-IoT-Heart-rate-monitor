################################################################################
#
# python-awsiotpythonsdk
#
################################################################################

PYTHON_AWSIOTPYTHONSDK_VERSION = 1.4.4
PYTHON_AWSIOTPYTHONSDK_SOURCE = AWSIoTPythonSDK-$(PYTHON_AWSIOTPYTHONSDK_VERSION).tar.gz
PYTHON_AWSIOTPYTHONSDK_SITE = https://files.pythonhosted.org/packages/95/1d/40c13828f8cec38b4ca4213b9815d19f4776de17bb82f9680b9297925ca9
PYTHON_AWSIOTPYTHONSDK_SETUP_TYPE = distutils
PYTHON_AWSIOTPYTHONSDK_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
