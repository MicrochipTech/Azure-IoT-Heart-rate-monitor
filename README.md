***Note: This demo/tool uses a WILC driver from the deprecated repository linux4wilc. The new driver repository is located at [linux4sam]( https://github.com/linux4sam/linux-at91/tree/master/drivers/net/wireless/microchip).***

# Azure-IoT-Heart-rate-monitor
Monitor heart rate with Linux/python based code using Azure IoT hub and web apps.

# Setup options

**1. SAMA5D27-SOM1-EK:**

- SAMA5D2 SOM EK:
https://www.microchip.com/DevelopmentTools/ProductDetails/PartNO/ATSAMA5D27-SOM1-EK1
- WILC1000 or WILC3000:
https://www.microchip.com/developmenttools/ProductDetails/AC164158
- Mikroe-2000 heart rate click board:
https://www.mikroe.com/heart-rate-click

<img src="images/sama5d27-som1-ek.png" width="500" >

**2. SAMA5D27-WLSOM1-EK:**

- SAMA5D2 WLSOM EK:
- Mikroe-2000 heart rate click board:
https://www.mikroe.com/heart-rate-click

<img src="images/sama5d27-wlsom1-ek.png" width="500" >

# Demo images

**For SAMA5D27-SOM1-EK:**
- SD card image based on python 2.7 [here](https://microchiptechnology.sharepoint.com/:u:/s/MWS/EVd4iN6guzFMtNAh665ZllsBRVLr4-j4aDYehvdxCxIZtg?e=DbfxAn)
- SD card image based on python 3.6 [here](https://microchiptechnology.sharepoint.com/:u:/s/MWS/EbVm2gyXFCxHspNpSImwc1IBDv2wu6Q2De5Es9YzRMVl1g?e=UZFwHK)

**For SAMA5D27-WLSOM1-EK:**
- SD card image based on python 3.6 [here](https://microchiptechnology.sharepoint.com/:u:/s/MWS/EcHrJHDDnPhIjMWpCz7iABwBJEcWlRgyuEYdNCve47M2LQ?e=GensV5)

Flash the SD card image into a micro SD card using etcher:
https://www.balena.io/etcher/

Username: root

# Connect to Wi-Fi

1. Make sure WILC SD is inserted (if using SAMA5D27-SOM1-EK).
2. The image will connect automatically to the following credentials:
**SSID**: MASTERS
**Passphrase**: microchip 
3. if the AP was not up at boot, or you wish to connect to another AP, use:
   > * killall wpa_supplicant udhcpc
   > * cd iot8 
   > * ./start_sta_pass_args.sh SSID Password
 
# Heart rate monitoring
1. Edit demo/SendDataToAzureCloud.py line 20 with your device connection string
2. Edit demo/SendDataToAzureCloud.py line 91 with your device ID
3. Edit Heart-rate-web-app/public/javascript/index.js line 136 with the device ID
4. Create an Azure Webapp with the repo at Heart-rate-web-app follow this (tutorial|https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-live-data-visualization-in-web-apps)

# Sample output
<img src="images/bmp_and_die_temperature.png" width="800" >
<img src="images/beats.png" width="800" >

# Build instructions
If you need to change/build-up on the demo, then you need bascially to get the suitable Linux4sam buildroot, clone current repo, add your changes to the external buildroot found under current repo and then rebuild. Please follow the following steps:
1. Clone Linux4sam buildroot:
   - For SAMA5D27-SOM1-EK: 
     > clone https://github.com/linux4sam/buildroot-at91.git -b linux4sam_6.0
   - For SAMA5D27-WLSOM1-EK: 
     > clone https://github.com/linux4sam/buildroot-at91.git -b sama5d27wlsom1ek_1.0
2. Get the external buildroot by cloning this repo:
   > clone https://github.com/MicrochipTech/Azure-IoT-Heart-rate-monitor.git
3. Navigate to buildroot directory:
   > cd buildroot-at91/
4. Make sure you really cloned the suitable tag:
   >  git branch
5. Do your modifications as desired in external buildroot Azure-IoT-Heart-rate-monitor/buildroot_external/
6. Build buildroot using your modified external buildroot:
   - For SAMA5D27-SOM1-EK:
     > BR2_EXTERNAL=../Azure-IoT-Heart-rate-monitor/buildroot_external/ make sama5d27_som1_ek_wilc_defconfig
   - For SAMA5D27-WLSOM1-EK:
     > BR2_EXTERNAL=../Azure-IoT-Heart-rate-monitor/buildroot_external/ make sama5d27_wlsom1_ek_defconfig
   - Then,
     > make
     
# Have questions/comments?
Feel free to reach out to and amr.sayed@microchip.com
