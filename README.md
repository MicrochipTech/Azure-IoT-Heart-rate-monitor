# Azure-IoT-Heart-rate-monitor
Monitor heart rate using Azure IoT hub and web apps


**The project uses:**

- SAMA5D2 SOM EK:
https://www.microchip.com/DevelopmentTools/ProductDetails/PartNO/ATSAMA5D27-SOM1-EK1

- WILC1000 or WILC3000:
https://www.microchip.com/developmenttools/ProductDetails/AC164158

- Mikroe-2000 heart rate click board:
https://www.mikroe.com/heart-rate-click

![image](https://user-images.githubusercontent.com/44651700/58664573-cb35d280-82e3-11e9-8b88-c12f34b2e68e.png)

# Download SD card demo image from:

**For SAMA5D27-SOM1-EK:**

- SD card image based on python 2.7:
https://microchiptechnology-my.sharepoint.com/:u:/g/personal/amr_sayed_microchip_com/EdWcwHJN5LtLs46PX2JcC14BeDvpJ_0lPJGyeqve5EsJxg?download=1

- SD card image based on python 3.6:
https://microchiptechnology-my.sharepoint.com/:u:/g/personal/amr_sayed_microchip_com/EVdhOE3SZ7JGtXboZA2t1J8BAw0J9D9hu2ZUVzz7B4hM1w?download=1

**For SAMA5D27-WLSOM1-EK:**

- SD card image based on python 3.6:
https://microchiptechnology-my.sharepoint.com/:u:/g/personal/amr_sayed_microchip_com/EZ3m_19-bXNIlJgBcuhVaH8Bw3zFIO1dOErn56MOrKWr9Q?download=1

Flash the SD card image into a micro SD card using etcher:
https://www.balena.io/etcher/

username: root

# Connect to Wi-Fi

Make sure WILC SD is inserted, Make sure the AP has the following:

**SSID**: MASTERS
**Passphrase**: microchip

The image will auto connect to the above on boot. 

if the AP was not up at boot, or you wish to connect to another AP, use:
1. killall wpa_supplicant udhcpc
2. cd iot8
3. ./start_sta_pass_args.sh SSID Password

# Heart rate monitoring
1. Edit demo/SendDataToAzureCloud.py line 20 with your device connection string
2. Edit demo/SendDataToAzureCloud.py line 91 with your device ID
3. Edit Heart-rate-web-app/public/javascript/index.js line 136 with the device ID
4. Create an Azure Webapp with the repo at Heart-rate-web-app follow this (tutorial|https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-live-data-visualization-in-web-apps)
