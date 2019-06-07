################################################################################
#
# web-socket
#
################################################################################

WEBSOCKET_VERSION = 1
WEBSOCKET_SITE = $(BR2_EXTERNAL_HRWILC_PATH)/package/websocket
WEBSOCKET_SITE_METHOD = local

define WEBSOCKET_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)
endef

define WEBSOCKET_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0777 $(@D)/websocket \
		$(TARGET_DIR)/root/
endef

$(eval $(generic-package))
