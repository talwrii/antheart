"""
    Code based on:
        https://github.com/mvillalba/python-ant/blob/develop/demos/ant.core/03-basicchannel.py
    in the python-ant repository and
        https://github.com/tomwardill/developerhealth
    by Tom Wardill
"""
import contextlib
import logging
import Queue
import threading

from ant.core import driver, event, message, node
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER

LOGGER = logging.getLogger('heart')

SERIAL = '/dev/ttyUSB0'
NETKEY = 'B9A521FBBD72C345'.decode('hex')

@contextlib.contextmanager
def with_heart_rate_queue():
    "Return a queue object that gives heart rates"
    with HeartRateMonitor(serial=SERIAL, netkey=NETKEY) as hrm:
        q = Queue.Queue()
        hrm.start(callback=q.put)
        try:
            yield q
        finally:
            hrm.stop()

def heart_rate_stream():
    "Iterator of heart rates"
    with with_heart_rate_queue() as q:
        yield q.get()

class HeartRateMonitor(event.EventCallback):
    # Adapted from J Bader code sample (see README.md)
    def __init__(self, serial, netkey):
        self.serial = serial
        self.netkey = netkey
        self.antnode = None
        self.channel = None
        self.callback = None
        self.lock = threading.RLock()

    def start(self, callback=None):
        LOGGER.debug("starting node")
        if callback:
            self._set_callback(callback)

        self._start_antnode()
        self._setup_channel()
        self.channel.registerCallback(self)
        LOGGER.debug("start listening for hr events")

    def stop(self):
        if self.channel:
            self.channel.close()
            self.channel.unassign()
        if self.antnode:
            self.antnode.stop()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if self.antnode and self.antnode.running:
            self.stop()

    def _start_antnode(self):
        stick = driver.USB2Driver(self.serial)
        self.antnode = node.Node(stick)
        self.antnode.start()

    def _setup_channel(self):
        key = node.NetworkKey('N:ANT+', self.netkey)
        self.antnode.setNetworkKey(0, key)
        self.channel = self.antnode.getFreeChannel()
        self.channel.name = 'C:HRM'
        self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(120, 0, 0)
        self.channel.setSearchTimeout(TIMEOUT_NEVER)
        self.channel.setPeriod(8070)
        self.channel.setFrequency(57)
        self.channel.open()

    def process(self, msg):
        with self.lock:
            if isinstance(msg, message.ChannelBroadcastDataMessage):
                heart_rate = ord(msg.payload[-1])
                LOGGER.debug('Read heart rate: %r', heart_rate)
                if self.callback:
                    self.callback(heart_rate)
                else:
                    print('Heart rate is {}'.format(heart_rate))

    def _set_callback(self, callback):
        with self.lock:
            self.callback = callback
