#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import time
import argparse
import subprocess

def build_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', '-i', type=int, default=100, help = "Interval of process check look in milliseconds")
    parser.add_argument('--watch', '-w', type=str, metavar = "FILENAME", help = "Watch memory usage and export to a file with gnuplot format")
    parser.add_argument('sub_command', nargs='*')
    return parser

def print_report(signalnum = None, stackframe = None):
    if not signalnum is None:
        print()
        os.kill(proc.pid, signalnum)
        proc.poll()

    if proc.returncode != 0:
        print('Command exited with non-zero status %d' % proc.returncode)

    print("%(command)s  VmPeak: %(VmPeak)s  VmHWM: %(VmHWM)s" % {
            'command' : ' '.join(sub_command),
            'VmPeak' : make_readable(status['VmPeak']),
            'VmHWM' : make_readable(status['VmHWM'])
          })

    exit(proc.returncode)

def make_readable(size_str):
    # size_str should be like "  1077992 kB"
    (size, kB) = tuple(size_str.strip().split(' '))
    size = float(size)
    return  ("%.1fkB" % size) if size < 1024 else\
            ("%.1fMB" % (size / 1024)) if size < 1024**2 else\
            ("%.1fGB" % (size / 1024**2)) if size < 1024**2 else\
            ("%.1fTB" % (size / 1024**3))

def size_to_int(size_str):
    # size_str should be like "  1077992 kB"
    return int(size_str.strip().split(' ')[0])

proc = None
sub_command = None
status = None

if __name__=="__main__":
    args = build_argparse().parse_args()
    sub_command = args.sub_command

    signal.signal(signal.SIGINT, print_report)
    signal.signal(signal.SIGTERM, print_report)

    proc = subprocess.Popen(args.sub_command)
    proc_path = "/proc/" + str(proc.pid) + "/status"

    watch_file = open(args.watch, 'w') if args.watch is not None else None
    begin_time = time.time()

    while proc.poll() != 0:
        with open(proc_path, 'r') as f:
            status = dict([tuple(line.split(':')) for line in f.read().splitlines()])
            if watch_file is not None:
                watch_file.write("%(elapsed_sec)f %(VmHWM)d\n" % {
                    'elapsed_sec': time.time() - begin_time,
                    'VmHWM': size_to_int(status['VmHWM'])
                    })
        time.sleep(args.interval / 1000.0)

    print_report()
