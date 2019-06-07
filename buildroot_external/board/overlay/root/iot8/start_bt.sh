#!/bin/bash
echo BT_POWER_UP > /dev/wilc_bt
sleep 1
echo BT_DOWNLOAD_FW > /dev/wilc_bt
sleep 1
hciattach ttyS1 any 115200 noflow
sleep 2
ln -svf /usr/libexec/bluetooth/bluetoothd /usr/sbin
bluetoothd -n &
sleep 2
hciconfig hci0 up
sleep 1
hciconfig
hciconfig hci0 leadv &
sleep 2
cd /usr/sbin
./btgatt-server -i hci0 -s low -t public -r -v
