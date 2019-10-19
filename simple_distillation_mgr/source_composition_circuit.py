#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Source Composition Control Circuit Thread """

__author__ = "Yaroslav Kholod"
__copyright__ = "Copyright 2019, The Kettlebell project"
__credits__ = "Yaroslav Kholod"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Yaroslav Kholod"
__email__ = "pretorian.yaroslav@gmail.com"
__status__ = "Development"

import threading
import time
import os
import signal
import sys
sys.path.insert(1, '/kettlebell-riak-driver')
from parameters import parameter
import data_table

class sourceCompositionCircuit (threading.Thread):
    def __init__(self, threadID, columnId):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "sourceComposition"
    def run(self):
        print("Starting " + self.name)
