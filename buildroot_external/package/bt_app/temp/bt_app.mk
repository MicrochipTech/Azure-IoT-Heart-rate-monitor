################################################################################
#
# BT Application
#
################################################################################

BT_APP_VERSION = 1
BT_APP_SITE = $(BR2_EXTERNAL_HRWILC_PATH)/package/bt_app
BT_APP_SITE_METHOD = local

define BT_APP_BUILD_CMDS
        $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)
endef

define BT_APP_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0777 $(@D)/../bluez5_utils-5.48/tools/btgatt-server \
		$(TARGET_DIR)/usr/sbin
endef

$(eval $(generic-package))
