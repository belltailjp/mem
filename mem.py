#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse
import subprocess

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sub_command', nargs='*')
    args = parser.parse_args()

    proc = subprocess.Popen(args.sub_command)
    proc_path = "/proc/" + str(proc.pid) + "/status"
    status = dict()
    while proc.poll() != 0:
        with open(proc_path, 'r') as f:
            status = dict([tuple(line.rstrip().split(':')) for line in f.readlines()])
        time.sleep(0.1)

    print('VmPeak', status['VmPeak'])
    print('VmSize', status['VmSize'])
