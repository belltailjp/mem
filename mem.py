#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import argparse
import subprocess

def print_report(signalnum = None, stackframe = None):
    if not signalnum is None:
        print()
        os.kill(proc.pid, signalnum)

    if proc.poll() is not None and proc.returncode != 0:
        print('Command exited with non-zero status %d' % proc.returncode)

    (user, system, children_user, children_system, elapsed) = os.times()
    print("%(command)s  VmPeak: %(VmPeak)s  VmHWM: %(VmHWM)s  user: %(user).2fs  system: %(system).2fs  total: %(total).2fs" % {
            'command' : ' '.join(sub_command),
            'VmPeak' : make_readable(status['VmPeak']),
            'VmHWM' : make_readable(status['VmHWM']),
            'user' : children_user,
            'system' : children_system,
            'total' : time.time() - begin_time
          })

    exit(proc.returncode)

def make_readable(size_str):
    # size_str should be like "  1077992 kB"
    (size, kB) = tuple(size_str.strip().split(' '))
    size = float(size)
    return  ("%.1fkB" % size) if size < 1024 else\
            ("%.1fMB" % (size / 1024)) if size < 1024**2 else\
            ("%.1fGB" % (size / 1024**2)) if size < 1024**3 else\
            ("%.1fTB" % (size / 1024**3))

def size_to_int(size_str):
    # size_str should be like "  1077992 kB"
    return int(size_str.strip().split(' ')[0])

begin_time = None
proc = None
sub_command = None
status = None

class PartialArgumentParser(argparse.ArgumentParser):
    def __custom_error(self, message):
        raise SystemExit()

    def __custom_exit(self, status = 0, message = None):
        raise SystemExit()

    def __validate(self, argv):
        error_func, self.error = self.error, self.__custom_error

        valid = True
        try:
            self.parse_args(argv)

        except SystemExit:
            valid = False

        self.error = error_func
        return valid

    def best_known_args(self, argv = sys.argv[1:]):
        exit_func, self.exit = self.exit, self.__custom_exit
        _argv = argv
        while 0 <= len(_argv):
            if self.__validate(_argv):
                self.exit = exit_func
                return (self.parse_args(_argv), argv[len(_argv):])
            _argv = _argv[:-1]
            
        self.exit = exit_func
        print('Argument Error!!')

def build_argparse():
    parser = PartialArgumentParser()
    parser.add_argument('--interval', '-i', type=int, default=100, help = "Interval of process check look in milliseconds")
    parser.add_argument('--watch', '-w', type=str, metavar = "FILENAME", help = "Watch memory usage and export to a file with gnuplot format")
    return parser


if __name__=="__main__":
    (args, sub_command) = build_argparse().best_known_args()

    signal.signal(signal.SIGINT, print_report)
    signal.signal(signal.SIGTERM, print_report)

    try:
        proc = subprocess.Popen(sub_command)
        proc_path = "/proc/" + str(proc.pid) + "/status"

    except OSError as e:
        print(sys.argv[0] + ': cannot run ' + sub_command[0] + ': ' + e.strerror)
        exit(1)

    watch_file = open(args.watch, 'w') if args.watch is not None else None
    begin_time = time.time()
    if watch_file is not None:
        watch_file.write('#gnuplot\n')
        watch_file.write('#> plot "%(fn)s" using 1:2 w l t "VmSize", "%(fn)s" using 1:3 w l t "VmRSS"\n' % {'fn' : args.watch})
        watch_file.write('#time(sec) VmSize VmRSS(resident)\n')

    while proc.poll() is None:
        with open(proc_path, 'r') as f:
            status = dict([tuple(line.split(':')) for line in f.read().splitlines()])
            if watch_file is not None:
                watch_file.write("%(elapsed_sec)f %(VmSize)d %(VmRSS)d\n" % {
                    'elapsed_sec': time.time() - begin_time,
                    'VmSize': size_to_int(status['VmSize']),
                    'VmRSS': size_to_int(status['VmRSS'])
                    })
                watch_file.flush()
        time.sleep(args.interval / 1000.0)

    print_report()
