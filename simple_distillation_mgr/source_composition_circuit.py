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
from column_ctrl_mgr import ColumnCtrlMgr
from common_import import mixture
import data_table
import PID

column_ctrl_mgr = ColumnCtrlMgr()
maxCubeTemp = 97 # When do we stop in Celsius

class sourceCompositionCircuit(threading.Thread):
    """ Bottom column temperature manager.
        Temperature is controlled by simple PID algorithm """

    def __init__(self, threadID, columnId):
        """ Initialize Control Circuit variables and set parameters """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = u"sourceComposition"

        # Get required distillate quality and mash data
        column_data = column_ctrl_mgr.RowGet(columnId)
        self.distillateQuality = round(column_data[parameter.ColumnCtrlParams["distilateConcentration"]])
        self.mashVolume = column_data[parameter.ColumnCtrlParams["mashVolume"]] * 10
        self.mashConcentration = column_data[parameter.ColumnCtrlParams["mashConcentration"]]
        self.mashSpiritVolume = (self.mashConcentration * self.mashVolume) / 100

        # Configure PID parameters
        self.pid = PID.PID(3, 0, 0) # TBD ykholod: adjust to particular column. Probably Lastovyak can help!
        self.pid.setSampleTime(1) # PID computes new value each 1 sec

    def run(self):
        """ Bottom column temperature manager main loop """
        while 1:
            # Read CubeTemp
            temperature = data_table.dataTableGet(parameter.TopTempCels)

            self.pid.SetPoint = maxCubeTemp # Set ideal CubeTemp

            self.pid.update(temperature)
            powerValue = int(self.pid.output)
            powerValue = max(min(powerValue, 75 ), 30)

            # Apply power setting
            data_table.dataTableSet(parameter.PowerControl, powerValue)

            # Exit condition: When CubeTemp gets to maxCubeTemp
            if temperature >= maxCubeTemp:
                data_table.dataTableSet(parameter.PowerControl, 0) # Set power off
                sys.exit(0)

            time.sleep(1)

        return
