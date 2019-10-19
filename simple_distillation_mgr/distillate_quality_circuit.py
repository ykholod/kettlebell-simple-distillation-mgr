#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Distillate Quality Control Circuit Thread """

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
from column_ctrl_mgr import ColumnCtrlMgr
from common_import import mixture
import data_table
import PID

column_ctrl_mgr = ColumnCtrlMgr()

class distillateQualityCircuit (threading.Thread):
    """ Top column temperature manager. Temperature is controlled by simple PID algorithm """

    def __init__(self, threadId, columnId):
        """ Initialize Control Circuit variables and set parameters """
        threading.Thread.__init__(self)
        self.threadID = threadId
        self.name = u"distillateQuality"

        # Get required distillate quality
        column_data = column_ctrl_mgr.RowGet(columnId)
        distillateQuality = round(column_data[parameter.ColumnCtrlParams["distilateConcentration"]])

        # Configure PID parameters
        self.pid = PID.PID(10, 1, 1) # TBD ykholod: adjust to particular column. Probably Lastovyak can help!
        self.pid.SetPoint = mixture.vle_data_dew[distillateQuality] # Set ideal TopTemp for our quality
        self.pid.setSampleTime(10) # PID computes new value each 10 sec

    def run(self):
        """ Top column temperature manager main loop """
        while 1:
            # Read TopTemp
            temperature = data_table.dataTableGet(parameter.TopTempCels)

            self.pid.update(temperature)
            coolerValue = int(self.pid.output)
            coolerValue = max(min(coolerValue, 100 ), 10)

            # Apply cooler setting
            data_table.dataTableSet(parameter.ControlPump, coolerValue)

            # Exit condition: When power is set to 0, exit
            power = data_table.dataTableGet(parameter.PowerControl)
            if power == 0:
                sys.exit(0)

            time.sleep(1)
