#Copyright (c) Microchip. All rights reserved.

#Import needed python packages
import sys
import time                                    #For delays and getting current time
import smbus
from array import array                        #For handling samples
import statistics                            #For signal filtration
import MAX30100_definitions as MAX30100        #MAX30100 registers definitions

#Python SMBUS for I2C connection to click board
SMBUS_ID = 2                                #Bus ID (1 or 2)
bus = smbus.SMBus(SMBUS_ID)                    #Bus on which click board is connected

#Define needed variables
ALPHA = 0.95                                #For DC filter
dcw = 0
old_dcw = 0
bw_filter_val0 = 0
bw_filter_val1 = 0
index = 0
SAMPLES_BUFFER_SIZE = 500
samples = []
timestamps = []
bpm = []
peaks = 0
peak_det = 0
peak0_timestamp = 0
peak1_timestamp = 0
BPM_MAGIC_THRESH = 40                        #Magic threshold for counting a pulse as a peak
RET_ERROR = -1
RET_SUCCESS = 0

#Each sample is 4 bytes; 0,1 for IR LED and 2,3 for red LED
class SAMPLE: 
    def __init__(self): 
        self.ir = -1
        self.red = -1

class HEART_RATE:
    def __init__(self):
        self.beats = []
        self.bpm = 0
        
#Reporting error handler 
#For INTERNAL USE by the module and shouldn't be exported.       
def report_error(err):
    print ("ERR: " + err)

#Read status register  
#For INTERNAL USE by the module and shouldn't be exported.  
def get_status():
    status = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.INT_STATUS)
    return status

#Read MAX30100 FW version  
#For INTERNAL USE by the module and shouldn't be exported.  
def get_revision_ID():
    rev_id = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.REVISION_ID)
    return rev_id

#Read MAX30100 part ID 
#For INTERNAL USE by the module and shouldn't be exported.    
def get_part_ID():
    part_id = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.PART_ID)
    return part_id

#Reset
#For INTERNAL USE by the module and shouldn't be exported.    
def reset():
    timeout = 10
    mode_config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG)
    mode_config = mode_config | (1 << 6)
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG, mode_config)

    while timeout:
        mode_config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG)
        if (mode_config & 0x40) == 0:
            break
        else:
            time.sleep(0.01)
            timeout -= 1
    if timeout == 0:
        report_error("board reset")
        return RET_ERROR

    time.sleep(0.05)
    return RET_SUCCESS

#initialize
#For INTERNAL USE by the module and shouldn't be exported.
def initialize():
    timeout = 20
    config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG)
    config = (config & ~0x07) | MAX30100.TEMP_EN
    config = (config & ~0x07) | MAX30100.SPO2_EN
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG, config)

    config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.SPO2_CONFIG)
    #config |= MAX30100.SPO2_HI_RES_EN
    config |= MAX30100.SAMPLES_100
    config |= MAX30100.PULSE_WIDTH_1600
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.SPO2_CONFIG, config)

    config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.LED_CONFIG)
    config |= MAX30100.IR_CURRENT_500
    config |= MAX30100.RED_CURRENT_500
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.LED_CONFIG, config)

    config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.INT_ENABLE)
    config |= MAX30100.ENA_A_FULL
    config |= MAX30100.ENA_HR
    #config |= MAX30100.ENA_SO2
    config |= MAX30100.ENA_TEMP
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.INT_ENABLE, config)    
        
    while timeout:
        status = get_status()
        if (status & MAX30100.A_FULL) == MAX30100.A_FULL:
            break
        else:
            time.sleep(0.01)
            timeout -= 1
    if timeout == 0:
        report_error("board init")
        return RET_ERROR
        
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.FIFO_WRITE_PTR, 0)
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.OVER_FLOW_CNT, 0)
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.FIFO_READ_PTR, 0)
    
    return RET_SUCCESS

#Remove DC component from a sample  
#For INTERNAL USE by the module and shouldn't be exported.  
def dc_remove(sample) :
    global dcw
    global old_dcw
    dcw = sample + ALPHA*old_dcw
    sample_dc_filtered = dcw - old_dcw
    old_dcw = dcw
    return sample_dc_filtered

#Low pass Butterworth filter 
#For INTERNAL USE by the module and shouldn't be exported.   
def low_pass_butterworth_filter(sample) :
    global bw_filter_val0
    global bw_filter_val1
    bw_filter_val0 = bw_filter_val1
    
    #Fs = 100Hz and Fc = 10Hz
    bw_filter_val1 = (2.452372752527856026e-1 * sample) + (0.50952544949442879485 * bw_filter_val0)
    
    sample_bw_filtered = bw_filter_val0 + bw_filter_val1
    return sample_bw_filtered

#Locate the peaks
#For INTERNAL USE by the module and shouldn't be exported.
def peak_detect(samples_arr) :
    peaks = 0
    peak_det = 0
    peaks_idxs = []
    i = 1
    j = 0
    while i < len(samples_arr):
        curr = samples_arr[i]
        prev = samples_arr[i-1]
        #print (str(curr))
        if curr > BPM_MAGIC_THRESH:
            if curr < prev:
                if peak_det == 0:
                    peak_det = 1
                    peaks += 1
                    peaks_idxs.append(i) 
        elif curr < 0:
            peak_det = 0
            
        i += 1
        
    return peaks_idxs
    
def process_peaks() :
    global samples
    global timestamps
    global peaks
    global peak_det
    global peak0_timestamp
    global peak1_timestamp
    curr_bpm = 0
    
    i = 1
    while i < len(samples):
        if samples[i] > BPM_MAGIC_THRESH:
            if samples[i] < samples[i-1]:
                if peak_det == 0:
                    peak_det = 1
                    if peaks == 0:
                        peak0_timestamp = timestamps[i-1]
                    elif peaks == 1:
                        peak1_timestamp = timestamps[i-1]
                    peaks += 1
        elif samples[i] < 0:
            peak_det = 0
                
        if peaks == 2:
            diff = peak1_timestamp - peak0_timestamp
            if diff != 0:
                curr_bpm = 60000/diff
                print (">>>> " + str(curr_bpm) + " .. " + str(len(bpm)))
            
            peaks = 1
            peak0_timestamp = peak1_timestamp
            
        i += 1
        
    if len(bpm) == 10:
        bpm.pop(0)
    bpm.append(curr_bpm)
        
#Set Red LED current
#Input:    
#    Value 0 -> 15  
#    Size: 4 bits
#    Mask [RED_CURRENT_MASK]: 0Xxxxx0000
#For INTERNAL USE by the module and shouldn't be exported.
def set_red_led_current(level):
    ''' - Set red LED current and hence intensity level
        - "level" value should vary between 0 (lowest) and 15 (highest)
        - Red led current affects measurement of SPO2 in SPO2 mode'''
    if level < (MAX30100.RED_CURRENT_0 >> 4) or level > (MAX30100.RED_CURRENT_500 >> 4):
        report_error("Red LED level set")
        return RET_ERROR
    else:
        led_config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.LED_CONFIG)
        led_config &= 0x0F
        led_config |= level << 4
        bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.LED_CONFIG, led_config)
        return RET_SUCCESS
        
#Set IR LED current
#Input: 
#    Value 0 -> 15  
#    Size: 4 bits
#    Mask [IR_CURRENT_MASK]: 0X0000xxxx
#For INTERNAL USE by the module and shouldn't be exported.
def set_ir_led_current(level):
    if level < MAX30100.IR_CURRENT_0 or level > MAX30100.IR_CURRENT_500:
        report_error("IR LED level set")
        return RET_ERROR
    else:
        led_config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.LED_CONFIG)
        led_config &= 0xF0
        led_config |= level
        bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.LED_CONFIG, led_config)
        return RET_SUCCESS

#Set SPO2 sampling rate
#Input: 
#    Value: Sampling rate value 0 -> 7 
#    Size: 3 bits
#    Mask [SAMPLES_MASK]: 0X000xxx00  
#For INTERNAL USE by the module and shouldn't be exported.    
def set_spo2_sr(sr):
    if sr < (MAX30100.SAMPLES_50 >> 2) or sr > (MAX30100.SAMPLES_1000 >> 2):
        report_error("SPO2 sampling rate set")
        return RET_ERROR
    else:
        spo2_config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.SPO2_CONFIG)
        spo2_config |= sr << 2
        bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.SPO2_CONFIG, spo2_config)
        return RET_SUCCESS

#Set LED (RED and IR) pulse width
#Input: 
#    Value: Pulse width value 0 -> 3 
#    Size: 2 bits
#    Mask [PULSE_WIDTH_MASK]: 0X000000xx 
#For INTERNAL USE by the module and shouldn't be exported.       
def set_led_pw(pw):
    if pw < MAX30100.PULSE_WIDTH_200 or pw > MAX30100.PULSE_WIDTH_1600:
        report_error("LED pulse width set")
        return RET_ERROR
    else:
        spo2_config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.SPO2_CONFIG)
        spo2_config |= pw
        bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.SPO2_CONFIG, spo2_config)
        return RET_SUCCESS

#Function returns single IR reading for HR calculation.
#Returned data to be filtered first before using it.
#For INTERNAL USE by the module and shouldn't be exported.
def get_ir_readings():
    timeout = 50
    sample = SAMPLE()

    while timeout:
        status = get_status()
        if (status & MAX30100.HR_RDY) == MAX30100.HR_RDY:
            break
        else:
            time.sleep(0.01)
            timeout -= 1
    if timeout == 0:
        report_error("HR read")
        return sample
        
    data = bus.read_i2c_block_data(MAX30100.I2C_ADR, MAX30100.FIFO_DATA_REG, 4)
    sample.ir = data[0] << 8 | data[1]
    return sample.ir


#Get beats readings for plotting purposes
#Function needs to wait at least one second to have enough samples for filtering purposes    
def get_beats():
    ''' - Return an array of heart rate readings for plotting purposes
        - You need to place your finger firmly on the sensor
        - take care as sensor reading is very sensitive to finger movements
        - You need to wait for 1 second for the function to collect enough samples
        - You have to call the function continuously for more reliable signal '''
    global samples
    global timestamps
    t0 = time.time()
    t1 = t0
    acquisition_time = 1    #1 second
    
    #Clear samples and timestamps history
    del samples[:]
    del timestamps[:]
    
    #Acquire samples for acquisition_time seconds
    while t1 < (t0 + acquisition_time):
        samples.append(get_ir_readings())
        timestamps.append(int(round(time.time() * 1000)))
        t1 = time.time()
    print ("Number of samples: " + str(len(samples)))
    
    #Pass signal through DC filter
    i = 0
    while i < len(samples):
        samples[i] = dc_remove(samples[i])
        i += 1
    
    #Calculate signal medium
    ir_median = statistics.median(samples)
    
    #Pass signal through median diff filter and then butterworth filter
    i = 0
    while i < len(samples):
        samples[i] = ir_median - samples[i]
        samples[i] = low_pass_butterworth_filter(samples[i])
        i += 1    

    #Return clean (filtered) signal
    return samples
  
#Calculate BPM
#Function needs to wait at least 10 seconds to get more accurate BPM
def calculate_bpm() :
    ''' - Calculate heart rate as BPM (bit per minute)
        - You need to place your finger firmly on the sensor
        - take care as sensor reading is very sensitive to finger movements
        - You need to wait for 15 seconds for the function to collect enough samples'''
    
    #List of BPMs acting as a history
    global bpm
    
    #Heart Rate object
    heart_rate = HEART_RATE()
    
    #Get a set of filtered samples
    get_beats()

    #Get an instantaneous BMP based of peaks timing
    process_peaks()
    
    #print ("### " + str(bpm_sum))    
    #Calculate avg BPM based on BPM history
    bpm_avg = 0
    if len(bpm) != 0:
        bpm_avg = sum(bpm) / len(bpm)
    
    #Return avg BPM
    heart_rate.beats = samples
    heart_rate.bpm = bpm_avg
    return heart_rate

#Read die temperature        
def read_temp():
    ''' - Read die temperature in degree Celsius 
        - Sensor is not very accurate '''
    timeout = 10
    error = -1
    config = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG)
    config = config | MAX30100.TEMP_EN
    bus.write_byte_data(MAX30100.I2C_ADR, MAX30100.MODE_CONFIG, config)
    
    while timeout:
        status = get_status()
        if (status & MAX30100.TEMP_RDY) == MAX30100.TEMP_RDY:
            break
        else:
            time.sleep(0.01)
            timeout -= 1
    if timeout == 0:
        report_error("Temperature read")
        return RET_ERROR
    
    temp_integer = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.TEMP_INTEGER)
    temp_fraction = bus.read_byte_data(MAX30100.I2C_ADR, MAX30100.TEMP_FRACTION)
    temp_fraction = round(temp_fraction * 0.0625,2)
    temp = temp_integer + temp_fraction   
    return temp

#Main function
# if __name__ == 'hr_click_board', executes on import
# if __name__ == '__main__', executes on direct run using command "python hr_click_board.py"
if __name__ == 'hr_click_board':
    #Banner
    print ( "########################################" )
    print ( "Python {0}".format(sys.version) )
    print ( "Heart Rate Click Board Python Controller" )
    
    #Get revision ID of MAX30100
    rev_id = get_revision_ID()
    print ("Click board FW Revision: " + hex(rev_id))
    
    #Get part ID of MAX30100
    part_id = get_part_ID()
    print ("Click board part ID: " + hex(part_id))
    
    print ( "########################################" )
    
    #Reset MAX30100
    reset()
    
    #Init MAX30100
    initialize()