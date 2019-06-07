################################################################################
#
# azure-iot-sdk-python
#
################################################################################

AZURE_IOT_SDK_PYTHON_VERSION = release_2019_01_03
AZURE_IOT_SDK_PYTHON_SITE = https://github.com/Azure/azure-iot-sdk-python
AZURE_IOT_SDK_PYTHON_SITE_METHOD = git
AZURE_IOT_SDK_PYTHON_GIT_SUBMODULES = YES
AZURE_IOT_SDK_PYTHON_INSTALL_STAGING = NO
AZURE_IOT_SDK_PYTHON_INSTALL_TARGET = YES
PYTHON_VERSION=3.6

#SDK features and options
AZURE_IOT_SDK_PYTHON_CONF_OPTS = -DCMAKE_SYSTEM_VERSION=4.9 -Drun_e2e_tests=OFF -Drun_sfc_tests=OFF -Drun_longhaul_tests=OFF -Duse_amqp=ON -Duse_http=ON -Duse_mqtt=ON -Ddont_use_uploadtoblob=OFF -Drun_unittests=OFF -Dbuild_python=$(PYTHON_VERSION) -Drun_valgrind=0 -Dtoolchainfile=" " -Dcmake_install_prefix=" " -Dno_logging=OFF -Duse_prov_client=ON  -Duse_edge_modules=ON -Dskip_samples=ON

#Package other kernel dependencies
AZURE_IOT_SDK_PYTHON_DEPENDENCIES = libxml2 openssl libcurl util-linux

$(eval $(cmake-package))

#Post-build hook: Copy missing dependency libraries to target
define AZURE_IOT_SDK_PYTHON_CP_MISSING_LIBS
	echo "Copy missing dep libraries to target"
	cp $(@D)/c/provisioning_client/deps/utpm/libutpm.so $(TARGET_DIR)/usr/lib/ 
	cp $(@D)/c/provisioning_client/deps/libmsr_riot.so $(TARGET_DIR)/usr/lib/
endef
AZURE_IOT_SDK_PYTHON_POST_BUILD_HOOKS += AZURE_IOT_SDK_PYTHON_CP_MISSING_LIBS

#Post-install-target hook: Move iothub_client and iothub_service_client libraries to target to python path on target
define AZURE_IOT_SDK_PYTHON_MV_IOTHUB_LIBS
	echo "Move iothub libraries to python"$(PYTHON_VERSION)" path on target"
	mv $(TARGET_DIR)/usr/lib/iothub_client.so $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION)/lib-dynload/ 
	mv $(TARGET_DIR)/usr/lib/iothub_service_client.so $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION)/lib-dynload/
endef
AZURE_IOT_SDK_PYTHON_POST_INSTALL_TARGET_HOOKS += AZURE_IOT_SDK_PYTHON_MV_IOTHUB_LIBS
