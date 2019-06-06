import SAMBA 3.2
import SAMBA.Connection.Serial 3.2
import SAMBA.Device.SAMA5D2 3.2

SerialConnection {
	//port: "ttyACM0"
	//port: "COM85"
	//baudRate: 57600

	device: SAMA5D2Xplained {
                /* override part of default config */
                config {
                        /* use SDCard socket */
                        sdmmc {
                                instance: 0
                        }
                }
        }

	onConnectionOpened: {
		initializeApplet("sdmmc")

		applet.write(0x00000, "sdcard.img", false)

		// initialize boot config applet
		initializeApplet("bootconfig")

		// Use BUREG0 as boot configuration word
		applet.writeBootCfg(BootCfg.BSCR, BSCR.fromText("VALID,BUREG0"))

		// Enable external boot on SDMMC1 IOSET1
		applet.writeBootCfg(BootCfg.BUREG0,
                        BCW.fromText("EXT_MEM_BOOT,UART1_IOSET1,JTAG_IOSET3," +
                                     "SDMMC1,SDMMC0,NFC_DISABLED," +
                                     "SPI1_DISABLED,SPI0_DISABLED," +
                                     "QSPI1_DISABLED,QSPI0_DISABLED"))
	}
}
