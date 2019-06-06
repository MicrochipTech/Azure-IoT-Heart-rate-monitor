I2C_ADR          = 0x57
#DATA_IS_READY()     ( DATA_READY == 0 )
#DATA_IS_NOT_READY() ( DATA_READY != 0 )

# registers' addresses
INT_STATUS       = 0x00
INT_ENABLE       = 0x01
FIFO_WRITE_PTR   = 0x02
OVER_FLOW_CNT    = 0x03
FIFO_READ_PTR    = 0x04
FIFO_DATA_REG    = 0x05
MODE_CONFIG      = 0x06
SPO2_CONFIG      = 0x07
LED_CONFIG       = 0x09
TEMP_INTEGER     = 0x16
TEMP_FRACTION    = 0x17
REVISION_ID      = 0xFE
PART_ID          = 0xFF

# mode configuration bits
TEMP_EN          = 0x08
HR_ONLY          = 0x02
SPO2_EN          = 0x03

# SpO2 configuration bits
SPO2_HI_RES_EN   = 0x40

# interrupt enable bits
ENA_A_FULL       = 0x80
ENA_TEMP          = 0x40
ENA_HR           = 0x20
ENA_SO2          = 0x10

# interrupt status bits
PWR_RDY          = 0x01
A_FULL           = 0x80
TEMP_RDY         = 0x40
HR_RDY           = 0x20
SPO2_RDY 		 = 0x10



# sample rate control bits [samples per second]
SAMPLES_MASK     = 0x1C # mask
SAMPLES_50       = 0x00
SAMPLES_100      = 0x04
SAMPLES_167      = 0x08
SAMPLES_200      = 0x0C
SAMPLES_400      = 0x10
SAMPLES_600      = 0x14
SAMPLES_800      = 0x18
SAMPLES_1000     = 0x1C

# LED pulse width control bits - pulse width [us]
PULSE_WIDTH_MASK = 0x03 # mask
PULSE_WIDTH_200  = 0x00 # 13-bit ADC resolution
PULSE_WIDTH_400  = 0x01 # 14-bit ADC resolution
PULSE_WIDTH_800  = 0x02 # 15-bit ADC resolution
PULSE_WIDTH_1600 = 0x03 # 16-bit ADC resolution

# LED current control bits [ma]
IR_CURRENT_MASK  = 0x0F # mask
IR_CURRENT_0     = 0x00 # 0.0 mA
IR_CURRENT_44    = 0x01 # 4.4 mA
IR_CURRENT_76    = 0x02 # 7.6 mA
IR_CURRENT_110   = 0x03 # 11.0 mA
IR_CURRENT_142   = 0x04 # 14.2 mA
IR_CURRENT_174   = 0x05 # 17.4 mA
IR_CURRENT_208   = 0x06 # 20.8 mA
IR_CURRENT_240   = 0x07 # 24.0 mA
IR_CURRENT_271   = 0x08 # 27.1 mA
IR_CURRENT_306   = 0x09 # 30.6 mA
IR_CURRENT_338   = 0x0A # 33.8 mA
IR_CURRENT_370   = 0x0B # 37.0 mA
IR_CURRENT_402   = 0x0C # 40.2 mA
IR_CURRENT_436   = 0x0D # 43.6 mA
IR_CURRENT_468   = 0x0E # 46.8 mA
IR_CURRENT_500   = 0x0F # 50.0 mA

RED_CURRENT_MASK = 0xF0 # mask
RED_CURRENT_0    = 0x00 # 0.0 mA
RED_CURRENT_44   = 0x10 # 4.4 mA
RED_CURRENT_76   = 0x20 # 7.6 mA
RED_CURRENT_110  = 0x30 # 11.0 mA
RED_CURRENT_142  = 0x40 # 14.2 mA
RED_CURRENT_174  = 0x50 # 17.4 mA
RED_CURRENT_208  = 0x60 # 20.8 mA
RED_CURRENT_240  = 0x70 # 24.0 mA
RED_CURRENT_271  = 0x80 # 27.1 mA
RED_CURRENT_306  = 0x90 # 30.6 mA
RED_CURRENT_338  = 0xA0 # 33.8 mA
RED_CURRENT_370  = 0xB0 # 37.0 mA
RED_CURRENT_402  = 0xC0 # 40.2 mA
RED_CURRENT_436  = 0xD0 # 43.6 mA
RED_CURRENT_468  = 0xE0 # 46.8 mA
RED_CURRENT_500  = 0xF0 # 50.0 mA

FIFO_DEPTH       = 0x10  # one sample are 4 bytes