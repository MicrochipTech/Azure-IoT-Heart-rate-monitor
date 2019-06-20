#!/bin/bash

# Verify passed arguments
if [ $# -lt 1 ]
then
	echo "Usage:"
	echo "./start_sta_pass_arg.sh SSID [PASSPHRASE]"
else
	# Edit wpa_supplicant.conf
	ssid=$1
	passphrase=$2
	echo "SSID: $ssid"
	echo "PASSPHRASE: $passphrase"
	echo "ctrl_interface=/var/run/wpa_supplicant" > /etc/wpa_supplicant.conf
	echo "ap_scan=1" >> /etc/wpa_supplicant.conf
	echo "network={" >> /etc/wpa_supplicant.conf
	echo "	ssid=\"$ssid\"" >> /etc/wpa_supplicant.conf
	if [ $# == 1 ]
	then
		echo "	key_mgmt=NONE" >> /etc/wpa_supplicant.conf
	else
		echo "	psk=\"$passphrase\"" >> /etc/wpa_supplicant.conf
	fi
	echo "}" >> /etc/wpa_supplicant.conf

	# Run wpa_supplicant
	ifconfig wlan0 up
	wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant.conf &
	udhcpc -i wlan0 &
fi
