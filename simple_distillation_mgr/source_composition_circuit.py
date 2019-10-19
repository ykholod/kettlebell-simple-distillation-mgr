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
        self.pid = PID.PID(10, 1, 1) # TBD ykholod: adjust to particular column. Probably Lastovyak can help!
        self.pid.setSampleTime(10) # PID computes new value each 10 sec

        # Column based parameters
        self.columnVolume = 0.628 # Max flegma volume

    def run(self):
        """ Bottom column temperature manager main loop """
        while 1:
            # Calculate and set ideal cube temperature
            distillateVolume = data_table.dataTableGet(parameter.DistillateFlowMeter)
            self.pid.SetPoint = self._idealTempCelsGet(distillateVolume) # Set ideal CubeTemp for our quality

            # Read CubeTemp
            temperature = data_table.dataTableGet(parameter.CubeTempCels)

            self.pid.update(temperature)
            powerValue = int(self.pid.output)
            powerValue = max(min(powerValue, 75 ), 30)

            # Apply power setting
            data_table.dataTableSet(parameter.PowerControl, powerValue)

            # Exit condition: When we have distilled enought spirit
            totalSpiritLosses = self._totalSpiritLossesGet(distillateVolume)
            if totalSpiritLosses > self.mashSpiritVolume:
                data_table.dataTableSet(parameter.PowerControl, 0) # Set power off
                sys.exit(0)

            time.sleep(1)

    def _totalSpiritLossesGet(self, distillateVolume):
        """ Calculate total spirit losses from mash """
        # Already distilled spirit
        distilledSpiritVolume = (distillateVolume * self.distillateQuality) / 100

        # Losses to athmosphere (assume they are 2% of distilled spirit)
        atmosphereLosses = distilledSpiritVolume * 0.02

        # Spirit in column (based on magic flegma numbers)
        spiritInColumnVolume = (self.columnVolume * (self.distillateQuality - self.mashConcentration)) / 100

        # Total spirit losses
        totalSpiritLosses = distilledSpiritVolume + atmosphereLosses + spiritInColumnVolume

        return totalSpiritLosses

    def _idealTempCelsGet(self, distillateVolume):
        """ Calculate ideal temperature in cube """
        # Already distilled spirit
        distilledSpiritVolume = (distillateVolume * self.distillateQuality) / 100

        # Losses to athmosphere (assume they are 2% of distilled spirit)
        atmosphereLosses = distilledSpiritVolume * 0.02

        # Spirit in column (based on magic flegma numbers)
        spiritInColumnVolume = (self.columnVolume * (self.distillateQuality - self.mashConcentration)) / 100

        # Total spirit losses
        totalSpiritLosses = distilledSpiritVolume + atmosphereLosses + spiritInColumnVolume

        if totalSpiritLosses < self.mashSpiritVolume:
            # Spirit left in cube and mash concentration
            mashSpiritLeftovers = self.mashSpiritVolume - totalSpiritLosses
            currentMashConcentration = (mashSpiritLeftovers / (self.mashVolume - distilledSpiritVolume - atmosphereLosses)) * 100

            # Get mash bubbling point ideal temperature
            idealTempCels = mixture.vle_data_bubble[round(currentMashConcentration)]
        else: # When everything is distilled out
            idealTempCels = 95.00

        return idealTempCels
