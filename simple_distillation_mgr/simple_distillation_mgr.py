#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Simple Distillation Manager """

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

import distillate_quality_circuit
import source_composition_circuit

# Thread list
threads = []

def main():
    # Create new threads
    thread1 = distillate_quality_circuit.distillateQualityCircuit(1)
    thread2 = source_composition_circuit.sourceCompositionCircuit(2)

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("Exiting Main Thread")

    # exit daemon
    os.kill(1, signal.SIGKILL)

if __name__ == "__main__":
    main()
