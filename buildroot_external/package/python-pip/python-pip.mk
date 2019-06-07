################################################################################
#
# python-pip
#
################################################################################

PYTHON_PIP_VERSION = 19.0.3
PYTHON_PIP_SOURCE = pip-$(PYTHON_PIP_VERSION).tar.gz
PYTHON_PIP_SITE = https://files.pythonhosted.org/packages/36/fa/51ca4d57392e2f69397cd6e5af23da2a8d37884a605f9e3f2d3bfdc48397
PYTHON_PIP_SETUP_TYPE = setuptools
PYTHON_PIP_LICENSE_FILES = LICENSE.txt src/pip/_vendor/lockfile/LICENSE src/pip/_vendor/idna/LICENSE.rst src/pip/_vendor/chardet/LICENSE src/pip/_vendor/urllib3/LICENSE.txt src/pip/_vendor/requests/LICENSE src/pip/_vendor/html5lib/LICENSE src/pip/_vendor/distlib/LICENSE.txt src/pip/_vendor/webencodings/LICENSE src/pip/_vendor/msgpack/COPYING src/pip/_vendor/pep517/LICENSE src/pip/_vendor/pkg_resources/LICENSE src/pip/_vendor/pytoml/LICENSE src/pip/_vendor/cachecontrol/LICENSE.txt src/pip/_vendor/progress/LICENSE src/pip/_vendor/colorama/LICENSE.txt src/pip/_vendor/packaging/LICENSE src/pip/_vendor/certifi/LICENSE

$(eval $(python-package))
