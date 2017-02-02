"""
    Code based on:
        https://github.com/mvillalba/python-ant/blob/develop/demos/ant.core/03-basicchannel.py
    in the python-ant repository and
        https://github.com/tomwardill/developerhealth
    by Tom Wardill
"""
import logging
import Queue
import sys
import time

from ant.core import driver, event, log, message, node
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER

LOGGER = logging.getLogger()


LOGGER.debug('')


class HRM(event.EventCallback):
    def __init__(self, serial, netkey, callback=None):
        self.serial = serial
        self.netkey = netkey
        self.antnode = None
        self.channel = None
        self.callback = callback

    def start(self):
        LOGGER.debug("starting node")
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
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            heart_rate = ord(msg.payload[-1])
            if self.callback:
                self.callback(heart_rate)
            else:
                print('Heart rate is {}'.format(heart_rate))

SERIAL = '/dev/ttyUSB0'
NETKEY = 'B9A521FBBD72C345'.decode('hex')

def heart_rate_stream():
    q = Queue.Queue()
    with HRM(serial=SERIAL, netkey=NETKEY, callback=q.put) as hrm:
        hrm.start()
        while True:
            rate = q.get()
            yield rate
