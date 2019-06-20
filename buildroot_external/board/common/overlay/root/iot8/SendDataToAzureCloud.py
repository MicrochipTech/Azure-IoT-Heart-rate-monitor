# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
import sys
import HRClickBoard as click

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "Enter device connection string here"

# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000
INTERVAL = 5
RECEIVE_CALLBACKS = 0
RECEIVE_CONTEXT = 0

# Define the JSON message to send to IoT Hub.
MSG_TXT = "{\"id\": %s,\"temperature\": %.2f,\"heartRate\": %.2f,\"beats\": %s}"

def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )

# Handle direct method calls from IoT Hub
def device_method_callback(method_name, payload, user_context):
    global INTERVAL
    print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s" % (method_name, payload) )
    device_method_return_value = DeviceMethodReturnValue()
    if method_name == "SetTelemetryInterval":
        try:
            INTERVAL = int(payload)
            # Build and send the acknowledgment.
            device_method_return_value.response = "{ \"Response\": \"Executed direct method %s\" }" % method_name
            device_method_return_value.status = 200
        except ValueError:
            # Build and send an error response.
            device_method_return_value.response = "{ \"Response\": \"Invalid parameter\" }"
            device_method_return_value.status = 400
    else:
        # Build and send an error response.
        device_method_return_value.response = "{ \"Response\": \"Direct method not defined: %s\" }" % method_name
        device_method_return_value.status = 404
    return device_method_return_value

def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client

def iothub_client_send_telemetry_run():

    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        # Set up the callback method for direct method calls from the hub.
        client.set_device_method_callback(
            device_method_callback, None)

        # Set up the callback for receive messages from the hub.
        client.set_message_callback(
            receive_message_callback, RECEIVE_CONTEXT)

        while True:
            # Build the message with simulated telemetry values.
            deviceid = '\"MyDevice\"'
            temperature = click.read_temp()
            heartRate = click.calculate_bpm().bpm
            beats = click.calculate_bpm().beats
            msg_txt_formatted = MSG_TXT % (deviceid, temperature, heartRate,beats)
            message = IoTHubMessage(msg_txt_formatted)

            # Add a custom application property to the message.
            # An IoT hub can filter on these properties without access to the message body.
            prop_map = message.properties()
            if temperature > 30:
              prop_map.add("temperatureAlert", "true")
            else:
              prop_map.add("temperatureAlert", "false")

            # Send the message.
            print( "Sending message: %s" % heartRate )
            client.send_event_async(message, send_confirmation_callback, None)
            #time.sleep(INTERVAL)
            

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient stopped" )

if __name__ == '__main__':
    print ( "Azure IoT Hub Lab" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_send_telemetry_run()
