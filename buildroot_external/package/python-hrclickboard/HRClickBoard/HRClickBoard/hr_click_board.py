#Copyright (c) Microchip. All rights reserved.
#Algorithms for filtering the signal are based on the following article:
#https://morf.lv/implementing-pulse-oximeter-using-max30100

#Import needed python packages
import sys
import time                                        #For delays and getting current time
import smbus
from array import array                            #For handling samples
import statistics                                #For signal filtration
from .MAX30100_definitions import *            #MAX30100 IC registers definitions

#Python SMBUS for I2C connection to click board
SMBUS_ID = 2                                    #Bus ID (1 or 2)
bus = smbus.SMBus(SMBUS_ID)                        #Bus on which click board is connected

#History of samples, timestamps and BPM
samples = []
timestamps = []
bpm = []

#DC filter
dc_filter = {
    "alpha": 0.95,
    "dcw": 0,
    "old_dcw": 0
}

#butterworth filter
bw_filter = {
    "v0": 0,
    "v1": 0
}

#Peak tracking
peak = {
    "count": 0,
    "detected": 0
}

#Peaks timestamps
peak_timestamp = {
    "v0": 0,
    "v1": 0
}
#Magic threshold for counting a pulse as a peak
BPM_MAGIC_THRESH = 100

#Buffer to store BPM history to get more reliable BPM value                          
BPM_BUFFER_SIZE = 10                        

#Return types
RET_ERROR = -1
RET_SUCCESS = 0

#Each sample is 4 bytes; 0,1 for IR LED and 2,3 for red LED
class SAMPLE: 
    def __init__(self): 
        self.ir = -1
        self.red = -1

#Actual value returned when calling calculate_bpm()
#'beats' is the buffered filtered signal and 'bpm' is heart rate beats per minute
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
    status = bus.read_byte_data(I2C_ADR, INT_STATUS)
    return status

#Read MAX30100 FW version  
#For INTERNAL USE by the module and shouldn't be exported.  
def get_revision_ID():
    rev_id = bus.read_byte_data(I2C_ADR, REVISION_ID)
    return rev_id

#Read MAX30100 part ID 
#For INTERNAL USE by the module and shouldn't be exported.    
def get_part_ID():
    part_id = bus.read_byte_data(I2C_ADR, PART_ID)
    return part_id

#Reset
#For INTERNAL USE by the module and shouldn't be exported.    
def reset():
    timeout = 10
    
    #Write reset bit
    mode_config = bus.read_byte_data(I2C_ADR, MODE_CONFIG)
    mode_config = mode_config | (1 << 6)
    bus.write_byte_data(I2C_ADR, MODE_CONFIG, mode_config)

    #Wait for reset operation to finish
    while timeout:
        mode_config = bus.read_byte_data(I2C_ADR, MODE_CONFIG)
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

#Initialize
#For INTERNAL USE by the module and shouldn't be exported.
def initialize():
    timeout = 20
    
    #Enable temperature and SPO2 mode
    config = bus.read_byte_data(I2C_ADR, MODE_CONFIG)
    config = (config & ~0x07) | TEMP_EN
    config = (config & ~0x07) | SPO2_EN
    bus.write_byte_data(I2C_ADR, MODE_CONFIG, config)

    #Set sampling rate and pulse width for IR and Red LEDs sampling
    config = bus.read_byte_data(I2C_ADR, SPO2_CONFIG)
    #config |= SPO2_HI_RES_EN
    config |= SAMPLES_100
    config |= PULSE_WIDTH_1600
    bus.write_byte_data(I2C_ADR, SPO2_CONFIG, config)

    #Set IR and Red LEDs current (directly affects HR and SPO2 reasings)
    config = bus.read_byte_data(I2C_ADR, LED_CONFIG)
    config |= IR_CURRENT_500
    config |= RED_CURRENT_500
    bus.write_byte_data(I2C_ADR, LED_CONFIG, config)

    #Enable interrupts as needed
    config = bus.read_byte_data(I2C_ADR, INT_ENABLE)
    config |= ENA_A_FULL
    config |= ENA_HR
    #config |= ENA_SO2
    config |= ENA_TEMP
    bus.write_byte_data(I2C_ADR, INT_ENABLE, config)    
        
    while timeout:
        status = get_status()
        if (status & A_FULL) == A_FULL:
            break
        else:
            time.sleep(0.01)
            timeout -= 1
    if timeout == 0:
        report_error("board init")
        return RET_ERROR
        
    bus.write_byte_data(I2C_ADR, FIFO_WRITE_PTR, 0)
    bus.write_byte_data(I2C_ADR, OVER_FLOW_CNT, 0)
    bus.write_byte_data(I2C_ADR, FIFO_READ_PTR, 0)
    
    return RET_SUCCESS
     
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
    if level < (RED_CURRENT_0 >> 4) or level > (RED_CURRENT_500 >> 4):
        report_error("Red LED level set")
        return RET_ERROR
    else:
        led_config = bus.read_byte_data(I2C_ADR, LED_CONFIG)
        led_config &= 0x0F
        led_config |= level << 4
        bus.write_byte_data(I2C_ADR, LED_CONFIG, led_config)
        return RET_SUCCESS
        
#Set IR LED current
#Input: 
#    Value 0 -> 15  
#    Size: 4 bits
#    Mask [IR_CURRENT_MASK]: 0X0000xxxx
#For INTERNAL USE by the module and shouldn't be exported.
def set_ir_led_current(level):
    if level < IR_CURRENT_0 or level > IR_CURRENT_500:
        report_error("IR LED level set")
        return RET_ERROR
    else:
        led_config = bus.read_byte_data(I2C_ADR, LED_CONFIG)
        led_config &= 0xF0
        led_config |= level
        bus.write_byte_data(I2C_ADR, LED_CONFIG, led_config)
        return RET_SUCCESS

#Set SPO2 sampling rate
#Input: 
#    Value: Sampling rate value 0 -> 7 
#    Size: 3 bits
#    Mask [SAMPLES_MASK]: 0X000xxx00  
#For INTERNAL USE by the module and shouldn't be exported.    
def set_spo2_sr(sr):
    if sr < (SAMPLES_50 >> 2) or sr > (SAMPLES_1000 >> 2):
        report_error("SPO2 sampling rate set")
        return RET_ERROR
    else:
        spo2_config = bus.read_byte_data(I2C_ADR, SPO2_CONFIG)
        spo2_config |= sr << 2
        bus.write_byte_data(I2C_ADR, SPO2_CONFIG, spo2_config)
        return RET_SUCCESS

#Set LED (RED and IR) pulse width
#Input: 
#    Value: Pulse width value 0 -> 3 
#    Size: 2 bits
#    Mask [PULSE_WIDTH_MASK]: 0X000000xx 
#For INTERNAL USE by the module and shouldn't be exported.       
def set_led_pw(pw):
    if pw < PULSE_WIDTH_200 or pw > PULSE_WIDTH_1600:
        report_error("LED pulse width set")
        return RET_ERROR
    else:
        spo2_config = bus.read_byte_data(I2C_ADR, SPO2_CONFIG)
        spo2_config |= pw
        bus.write_byte_data(I2C_ADR, SPO2_CONFIG, spo2_config)
        return RET_SUCCESS

#Remove DC component from an IR/Red LED sample  
#For INTERNAL USE by the module and shouldn't be exported.  
def dc_remove(sample) :
    global dc_filter
    dc_filter["dcw"] = sample + dc_filter["alpha"]*dc_filter["old_dcw"]
    sample_dc_filtered = dc_filter["dcw"] - dc_filter["old_dcw"]
    dc_filter["old_dcw"] = dc_filter["dcw"]
    return sample_dc_filtered

#Low pass Butterworth filter for an IR/RED LED sample
#For INTERNAL USE by the module and shouldn't be exported.   
def low_pass_butterworth_filter(sample) :
    global bw_filter
    bw_filter["v0"] = bw_filter["v1"]
    
    #Fs = 100Hz and Fc = 10Hz
    #bw_filter["v1"] = (2.452372752527856026e-1 * sample) + (0.50952544949442879485 * bw_filter["v0"])
    bw_filter["v1"] = (1.367287359973195227e-1 * sample) + (0.72654252800536101020 * bw_filter["v0"]);
    
    sample_bw_filtered = bw_filter["v0"] + bw_filter["v1"]
    return sample_bw_filtered
  
#Function returns single IR reading for HR calculation.
#Returned data to be filtered first before using it.
#For INTERNAL USE by the module and shouldn't be exported.
def get_ir_readings():
    timeout = 50
    sample = SAMPLE()

    #Wait for IR sample to be ready
    while timeout:
        status = get_status()
        #We acquire sample by sample not full FIFO (using A_FULL) to be able to have a timestamp for every single sample
        if (status & HR_RDY) == HR_RDY:
            break
        else:
            #This delay is tied to sampling rate (currently, SR=100 which means that we get on average a sample every 10ms.
            #That's why sleep here must be < 10ms. We chose 5ms to be on the safe side.
            time.sleep(0.005)      
            timeout -= 1
    if timeout == 0:
        report_error("HR read")
        return sample
    
    #Read IR sample    
    data = bus.read_i2c_block_data(I2C_ADR, FIFO_DATA_REG, 4)
    sample.ir = data[0] << 8 | data[1]
    return sample.ir

#Calculate BPM based on time difference between each two consecutive peaks
#For INTERNAL USE by the module and shouldn't be exported.
def process_peaks() :
    global samples
    global timestamps
    global peak
    global peak_timestamp
    curr_bpm = 0
    
    i = 1
    while i < len(samples):
    
        #Sample is above the threshold and less than the previous one; this is the peak we are looking for
        if samples[i] > BPM_MAGIC_THRESH and samples[i] < samples[i-1]:
            if peak["detected"] == 0:
                peak["detected"] = 1
                if peak["count"] == 0:
                    #First peak ever
                    peak_timestamp["v0"] = timestamps[i-1]
                elif peak["count"] == 1:
                    #Second peak
                    peak_timestamp["v1"] = timestamps[i-1]
                peak["count"] += 1
                    
        #Restart searching for a peak only if samples went below zero to avoid fault peaks 
        elif samples[i] < 0:
            peak["detected"] = 0
        
        #We counted two peaks thewn calculate time differnce between them        
        if peak["count"] == 2:
            diff = peak_timestamp["v1"] - peak_timestamp["v0"]
            if diff != 0:
                curr_bpm = 60000/diff
                print (">>>> " + str(curr_bpm) + " .. " + str(len(bpm)))
            
            #Store current peak to calculate time difference with the upcoming peak once we have it
            peak["count"] = 1
            peak_timestamp["v0"] = peak_timestamp["v1"]
            
        i += 1
    
    #Add the instantaneous BPM to BPM buffer (history). This helps with getting more stable BPM reading    
    if len(bpm) == BPM_BUFFER_SIZE:
        bpm.pop(0)
    bpm.append(curr_bpm)

#Get beats readings for plotting purposes
#Function needs to wait at least one second to have enough samples for filtering purposes    
def acquire_filtered_signal():
    global samples
    global timestamps
    t0 = time.time()
    t1 = t0
    acquisition_time = 1    #1 second (recommended minimum)
    
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
    
    #Calculate signal mean
    ir_mean = statistics.mean(samples)
    
    #Pass signal through mean diff filter and then butterworth filter
    i = 0
    while i < len(samples):
        samples[i] = ir_mean - samples[i]
        samples[i] = low_pass_butterworth_filter(samples[i])
        i += 1    
  
#Calculate BPM
#Function needs to wait at least 10 seconds to get more accurate BPM
def calculate_bpm() :
    ''' - Calculate heart rate as BPM (bit per minute)
        - Return HEART_RATE object: .bpm is BPM and .beats is the buffered filtered signal
        - You need to place your finger firmly and horizontally on the sensor
        - Take care as sensor reading is very sensitive to finger movements and position
        - You need to wait for about 1 seconds for the callee functions to collect enough samples'''
    
    #List of BPMs acting as a history
    global bpm
    
    #Heart Rate object
    heart_rate = HEART_RATE()
    
    #Get a set of filtered samples
    acquire_filtered_signal()

    #Get an instantaneous BMP based of peaks timing
    process_peaks()
    
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
    
    #Enable temperature reading
    config = bus.read_byte_data(I2C_ADR, MODE_CONFIG)
    config = config | TEMP_EN
    bus.write_byte_data(I2C_ADR, MODE_CONFIG, config)
    
    #Wait for temperature sample to be ready
    while timeout:
        status = get_status()
        if (status & TEMP_RDY) == TEMP_RDY:
            break
        else:
            time.sleep(0.01)
            timeout -= 1
    if timeout == 0:
        report_error("Temperature read")
        return RET_ERROR
    
    #Read temperature and round fractional part to two decimal points
    temp_integer = bus.read_byte_data(I2C_ADR, TEMP_INTEGER)
    temp_fraction = bus.read_byte_data(I2C_ADR, TEMP_FRACTION)
    temp_fraction = round(temp_fraction * 0.0625, 2)
    temp = temp_integer + temp_fraction   
    return temp
