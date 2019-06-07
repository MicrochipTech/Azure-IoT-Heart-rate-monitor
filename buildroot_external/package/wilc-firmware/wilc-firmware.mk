################################################################################
#
# wilc-firmware
#
################################################################################

WILC_FIRMWARE_VERSION = 15.2
WILC_FIRMWARE_SITE = https://github.com/linux4wilc/firmware/archive
WILC_FIRMWARE_SOURCE = wilc_linux_15_2.zip

WILC_FIRMWARE_LICENSE = PROPRIETARY

define WILC_FIRMWARE_EXTRACT_CMDS
	$(UNZIP) -d $(BUILD_DIR) $(DL_DIR)/$(WILC_FIRMWARE_SOURCE)
	mv $(BUILD_DIR)/firmware-wilc_linux_15_2/* $(@D)
	rmdir $(BUILD_DIR)/firmware-wilc_linux_15_2
endef

define WILC_FIRMWARE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/mchp/
	$(INSTALL) -D -m 0644 $(@D)/*.bin \
		$(TARGET_DIR)/lib/firmware/mchp/
endef

$(eval $(generic-package))
