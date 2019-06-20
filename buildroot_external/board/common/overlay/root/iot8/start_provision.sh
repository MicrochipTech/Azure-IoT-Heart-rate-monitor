#!/bin/sh
cat << 'EOT' > /etc/init.d/S85start_wlan 
#!/bin/sh
case "$1" in
        start)
                sh /root/start_ap.sh
                ;;
        stop)
                ifconfig wlan0 down
                ;;
esac
exit 0
EOT
chmod 0755 /etc/init.d/S85start_wlan
ifconfig wlan0 down
reboot

