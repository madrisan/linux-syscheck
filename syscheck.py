#!/usr/bin/env python

# Display memory/cpu usage and system uptime on Linux
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from __future__ import division

import os, platform, socket, sys
from datetime import timedelta

__author__ = "Davide Madrisan"
__copyright__ = "Copyright 2015 Davide Madrisan"
__license__ = "GPLv3"
__version__ = "1"
__email__ = "davide.madrisan.gmail.com"
__status__ = "Beta"

def _kernel_version():
    release = platform.release()
    if not release: return None

    item = release.split('.')
    majVersion = int(item[0])
    minVersion = int(item[1])
    patchVersion = int(item[2].split('-')[0])

    return (((majVersion) << 16) + ((minVersion) << 8) + (patchVersion))

def _readfile(filename):
    if not os.path.isfile(filename):
        die(1, 'No such file: ' + filename)
        return None
    fd = open(filename, 'r')
    try:
        content = fd.readlines()
    except:
        die(1, 'Error opening the file ' + filename)
    return content

def _cpu_count_logical():
    """Return the number of logical CPUs in the system."""
    try:
        return os.sysconf("SC_NPROCESSORS_ONLN")
    except ValueError:
        # as a second fallback we try to parse /proc/cpuinfo
        num = 0

        f = open('/proc/cpuinfo', 'rb')
        try:
            for line in f:
                if line.lower().startswith('processor'):
                    num += 1
        except:
            pass

        return num

def check_cpu():
    """Return Total CPU MHz, current utilization and number of logical CPU"""

    CPUMzTotal = CPUUtilization = 0
    cpuinfo = _readfile('/proc/cpuinfo')
    for line in cpuinfo:
        cols = line.split(':')
        if cols[0].strip() == 'cpu MHz':
            CPUMzTotal += int(cols[1].split('.')[0])

    cpustat = _readfile('/proc/stat')
    for line in cpustat:
        cols = line.split()
        if cols[0] == 'cpu':
           (User, Nice, Sys, Idle, IOWait, IRQ, SoftIRQ, Steal) = (
               int(cols[i]) for i in range(1,9))
        UserTot = User + Nice
        SystemTot = Sys + IRQ + SoftIRQ
        Ratio = UserTot + SystemTot + Idle + IOWait + Steal

    CPUUtilization = (100 - (100*Idle/Ratio))
    CPUNumber = _cpu_count_logical()

    return (CPUMzTotal, CPUUtilization, CPUNumber)

def check_memory():
    """Return Total Memory, Available Memory and percent Utilization"""

    MemAvailable = None

    meminfo = _readfile('/proc/meminfo')
    for line in meminfo:
        cols = line.split()
        if cols[0] == 'Active(file):'    : MemActiveFile = int(cols[1])
        elif cols[0] == 'MemAvailable:'  : MemAvailable = int(cols[1])
        elif cols[0] == 'MemFree:'       : MemFree = int(cols[1])
        elif cols[0] == 'Inactive(file):': MemInactiveFile = int(cols[1])
        elif cols[0] == 'MemTotal:'      : MemTotal = int(cols[1])
        elif cols[0] == 'SReclaimable:'  : MemSlabReclaimable = int(cols[1])

    if not MemAvailable:
        kernelVersion = _kernel_version()

        if kernelVersion < 132635:  # 2.6.27
            MemAvailable = MemFree
        else:
            MemMinFree = int(_readfile('/proc/sys/vm/min_free_kbytes')[0])
            MemWatermarkLow = MemMinFree * 5 / 4
            MemAvailable = MemFree \
                - MemWatermarkLow + MemInactiveFile + MemActiveFile \
                - min((MemInactiveFile + MemActiveFile) / 2, MemWatermarkLow) \
                + MemSlabReclaimable \
                - min(MemSlabReclaimable / 2, MemWatermarkLow)

        if MemAvailable < 0: MemAvailable = 0

    MemoryUsagePerc = 100 - (MemAvailable * 100 / MemTotal)

    return (MemTotal, MemAvailable, MemoryUsagePerc)

def check_uptime():
    uptime = _readfile('/proc/uptime')
    uptime_secs = float(uptime[0].split()[0])

    updays = int(uptime_secs / (60 * 60 * 24))
    upminutes = int(uptime_secs / 60)
    uphours = int(upminutes / 60) % 24
    upminutes = upminutes % 60

    return (str(timedelta(seconds = uptime_secs)), updays, uphours, upminutes)

def die(exitcode, message):
    "Print error and exit with errorcode"
    sys.stderr.write('pyoocs: Fatal error: %s\n' % message)
    sys.exit(exitcode)

def main():
    # CSVOUTPUT=1 ./syscheck.py --> Output in CSV Format
    EnvCSVOutput = os.environ.get('CSVOUTPUT', '')

    # Hostname and FQDN
    Hostname = socket.gethostname()
    FQDN = socket.getfqdn()
    # CPU utilization
    CPUMzTotal, CPUConsumption, CPUs = check_cpu()
    # Memory utilization
    MemTotal, MemAvailable, MemoryUsagePerc = check_memory()
    MemTotal_Mb = MemTotal / 1024
    # System Uptime
    SystemUptime, UpDays, UpHours, UpMinutes = check_uptime()

    if EnvCSVOutput:
        print "Hostname,FQDN,CPUMzTotal,CPUConsumption,CPUs,\
MemTotal(Mb),MemoryUsagePerc,UptimeDays\n\
%s,%s,%d,%.2f,%d,%d,%.2f,%s" % (
            Hostname, FQDN, CPUMzTotal, CPUConsumption, CPUs,
            MemTotal_Mb, MemoryUsagePerc, UpDays)
    else:
        print "Hostname        : %s (%s)" % (Hostname, FQDN)
        print "CPU Tot/Used    : %dMHz/%.2f%% (%dCPU(s))" %(
            CPUMzTotal, CPUConsumption, CPUs)
        print "Memory Tot/Used : %dMb/%.2f%%" % (MemTotal_Mb, MemoryUsagePerc)
        print "System uptime   : " + SystemUptime

if __name__ == '__main__':
    exitcode = 0
    try:
        main()
    except KeyboardInterrupt:
        die(3, 'Exiting on user request')
    sys.exit(exitcode)

# vim:ts=4:sw=4:et
