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

https://microchiptechnology-my.sharepoint.com/:u:/g/personal/amr_sayed_microchip_com/EdWcwHJN5LtLs46PX2JcC14B0T46rwroWwmYx9B66u8zHg?download=1

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
