# pyv6m Package

Package to control a V6M ethernet relay boards using Python.
I can't read Chinese on the controller, but the unit operates
nicely and can be configured using HTTP and controlled on port
1234.  It theoretically supports MQTT protocol, but I haven't
received that documentation yet.

The underlying command structure sent to the board is simple.
The following example would turn on relay 1, and turn off relay 3.
The remaining relays are left unchanged:
    setr=1x0xxxxxx

The board supports other controls:
* '0' - off
* '1' - on
* '2' - pulse (on, delay, off)
* '3' - toggle
* '4' - group 2 relays adjacent relays.  On if '4x', off if 'x4'.
    
This package only supports turning relays on and off through the
V6M.set_relay method.

The board also supports 8 inputs. As a default from the factory,
the inputs directly control the relays.  This can be disabled through
the web interface.  The state of the inputs can be read using the V6M.get_sensor
interface, or by setting the sensor_callback.

The board will not send immediate feedback when input levels changed,
so the board is polled every second.

# Example:

    from time import sleep
    from pyv6m import V6M
    
    hub = V6M( 'host.test.com', 1234 )

    # Turn the first relay on
    hub.set_relay( 0, True )

    # Pause for a second
    sleep(1.)

    # Turn the first relay off
    hub.set_relay( 0, False )

    # Close the interface
    hub.close()
