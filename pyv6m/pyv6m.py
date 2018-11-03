"""
pyv6m is a package for controlling a Chinesee import V6M 8-channel RJ45
(Ethernet) bank of relays.

The state for a relay isn't updated until a response from the board or a
polling request occurs.

Michael Dubno - 2018 - New York
"""

from threading import Thread
import time
import socket
import select
import logging
import json

_LOGGER = logging.getLogger(__name__)

RELAYS_PER_BOARD = 8
SENSORS_PER_BOARD = 8

POLLING_FREQ = 1.

class V6M(Thread):
    """Interface with a Pencom relay controller."""
    # pylint: disable=too-many-instance-attributes
    _polling_thread = None
    _socket = None
    _running = False
    _disconnected = False

    def __init__(self, host = '192.168.1.166', port = 1234, relay_callback=None, sensor_callback=None):
        Thread.__init__(self, target = self)
        self._host = host
        self._port = port
        self._relay_callback = relay_callback
        self._sensor_callback = sensor_callback

        self._connect()
        self._polling_thread = Polling(self, POLLING_FREQ)
        self._polling_thread.start()
        self.start()

    def _connect(self):
        try:
            self._socket = socket.create_connection((self._host, self._port))
            self._relay_states = [None for _ in range(RELAYS_PER_BOARD)]
            self._sensor_states = [None for _ in range(SENSORS_PER_BOARD)]
            self._disconnected = False
        except (BlockingIOError, ConnectionError, TimeoutError) as error:
            _LOGGER.error("Connection: %s", error)

    def set_relay(self, addr, state):
        """Turn a relay on/off."""
        mask = ''
        for relay in range(RELAYS_PER_BOARD):
            mask += ('1' if state else '0') if relay == addr else 'x'
        self.send('setr=' + mask)

    def get_relay(self, addr):
        """Get the relay's state."""
        return self._relay_states[addr]

    def get_sensor(self,addr):
        """Get the sensor's state."""
        return self._sensor_states[addr]

    def _update_relay_state(self, addr, new_state):
        old_state = self._relay_states[addr]
        if self._relay_callback:
            self._relay_callback(addr, old_state, new_state)
        self._relay_states[addr] = new_state

    def _update_sensor_state(self, addr, new_state):
        old_state = self._sensor_states[addr]
        if self._sensor_callback:
            self._sensor_callback(addr, old_state, new_state)
        self._sensor_states[addr] = new_state

    def send(self, command):
        """Send data to the relay controller."""
        # FIX: If it is a state changing command, perhaps buffer it
        # until reconnected
        try:
            self._socket.send((command+'\r').encode('utf8'))
        except:
            self._disconnected = True

    def run(self):
        self._running = True
        data = ''
        while self._running:
            try:
                readable, _, _ = select.select([self._socket], [], [], POLLING_FREQ)
            except socket.error as err:
                raise
            if len(readable) != 0:
                byte = self._socket.recv(1)
                if byte == b'}':
                    data += byte.decode('utf-8')
                    self._processReceivedData(data.strip())
                    data = ''
                elif byte == b'\r' or byte == b'\t':
                    pass
                else:
                    data += byte.decode('utf-8')
            if self._disconnected:
                self._connect()


    def _processReceivedData(self, data):
        try:
            res = json.loads(data)
            outp = res["output"]
            for relay in range(len(outp)):
                self._update_relay_state(relay, '1' == outp[relay])
            inp = res["input"]
            for sensor in range(len(inp)):
                self._update_sensor_state(sensor, '1' == inp[sensor])
        except ValueError:
            _LOGGER.error("Weird data: %s", data)

    def close(self):
        """Close the connection and running threads."""
        self._running = False
        if self._polling_thread:
            self._polling_thread.close()
            self._polling_thread = None
        if self._socket:
            time.sleep(POLLING_FREQ)
            self._socket.close()
            self._socket = None


class Polling(Thread):
    """Thread that asks for each board's status."""

    def __init__(self, v6m, delay):
        super(Polling, self).__init__()
        self._v6m = v6m
        self._delay = delay
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            self._v6m.send('state=?')
            time.sleep(self._delay)

    def close(self):
        self._running = False
