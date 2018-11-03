"""
Test the V6M interface.
"""
from time import sleep
from pyv6m import V6M

def _relay_callback(relay, old_value, new_value):
    print('Relay',  relay, old_value, new_value)

def _sensor_callback(sensor, old_value, new_value):
    print('Sensor', sensor, old_value, new_value)

def _main():
    hub = V6M('192.168.2.39', 1234, _relay_callback, _sensor_callback)
    for trial in range(8):
        hub.set_relay(trial, True)
        sleep(.5)
        hub.set_relay(trial, False)
        sleep(.5)
    sleep(10.)
    hub.close()


_main()
