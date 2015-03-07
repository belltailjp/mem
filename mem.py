#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse
import subprocess

def make_readable(size_str):
    # size_str should be like "  1077992 kB"
    (size, kB) = tuple(size_str.strip().split(' '))
    size = float(size)
    return  ("%.1fkB" % size) if size < 1024 else\
            ("%.1fMB" % (size / 1024)) if size < 1024**2 else\
            ("%.1fGB" % (size / 1024**2)) if size < 1024**2 else\
            ("%.1fTB" % (size / 1024**3))

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sub_command', nargs='*')
    args = parser.parse_args()

    proc = subprocess.Popen(args.sub_command)
    proc_path = "/proc/" + str(proc.pid) + "/status"
    status = dict()
    while proc.poll() != 0:
        with open(proc_path, 'r') as f:
            status = dict([tuple(line.split(':')) for line in f.read().splitlines()])
        time.sleep(0.1)

    print('VmPeak', make_readable(status['VmPeak']))
    print('VmSize', make_readable(status['VmSize']))
