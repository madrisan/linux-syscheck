#!/usr/bin/python

# Display memory/swap/cpu usage and system uptime on Linux
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from __future__ import division

import os, platform, socket, sys
from datetime import timedelta

__author__ = "Davide Madrisan"
__copyright__ = "Copyright 2015 Davide Madrisan"
__license__ = "GPLv3"
__version__ = "3"
__email__ = "davide.madrisan.gmail.com"
__status__ = "stable"

def _kernel_version():
    release = platform.release()
    if not release: return None

    item = release.split('.')
    majVersion = int(item[0])
    minVersion = int(item[1])
    patchVersion = int(item[2].split('-')[0])

    return (((majVersion) << 16) + ((minVersion) << 8) + (patchVersion))

def _readfile(filename, abort_on_error=True, header=False):
    if not os.path.isfile(filename):
        if abort_on_error:
            die(1, 'No such file: ' + filename)
        else:
            warning('No such file: ' + filename)
        return None

    fd = open(filename, 'r')
    try:
        if header:
            content = fd.readlines()[1:]
        else:
            content = fd.readlines()
    except:
        die(1, 'Error opening the file ' + filename)
    return content

def _perc(value, ratio, complement=False):
    percentage = 100 * value / ratio
    if complement:
        return 100 - percentage
    else:
        return percentage

def _sizeof_fmt(num, factor=1024.0, skip=1, suffix='B'):
    units = ['', 'k','m','g','t']
    for unit in units[skip:]:
        if abs(num) < factor:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= factor
    return "%.1f%s%s" % (num, 'p', suffix)

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

    CPUUtilization = _perc(Idle, Ratio, complement=True)
    CPUNumber = _cpu_count_logical()

    return (CPUMzTotal, CPUUtilization, CPUNumber)

def check_memory():
    """Return Total Memory, Memory Used and percent Utilization"""

    MemAvailable = None
    MemHugePagesTotal = MemAnonHugePages = 0
    MemHugePageSize = 0

    meminfo = _readfile('/proc/meminfo')
    for line in meminfo:
        cols = line.split()
        if cols[0] == 'Active(file):'     : MemActiveFile = int(cols[1])
        elif cols[0] == 'MemAvailable:'   : MemAvailable = int(cols[1])
        elif cols[0] == 'Cached:'         : MemCached = int(cols[1])
        elif cols[0] == 'MemFree:'        : MemFree = int(cols[1])
        elif cols[0] == 'Inactive(file):' : MemInactiveFile = int(cols[1])
        elif cols[0] == 'MemTotal:'       : MemTotal = int(cols[1])
        elif cols[0] == 'SReclaimable:'   : MemSlabReclaimable = int(cols[1])
        elif cols[0] == 'Hugepagesize:'   : MemHugePageSize = int(cols[1])
        elif cols[0] == 'HugePages_Total:': MemHugePagesTotal = int(cols[1])
        elif cols[0] == 'HugePages_Free:' : MemHugePagesFree = int(cols[1])
        elif cols[0] == 'AnonHugePages:'  : MemAnonHugePages = int(cols[1])

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

    MemUsed = MemTotal - MemFree - MemCached
    MemUsedPerc = _perc(MemAvailable, MemTotal, complement=True)

    if not MemHugePagesTotal:
        MemHugePagesTotal = MemHugePagesUsage = MemHugePagesUsagePerc = 0
    else:
        MemHugePagesUsage = MemHugePagesTotal - MemHugePagesFree
        MemHugePagesUsagePerc = (
            _perc(MemHugePagesUsage, MemHugePagesTotal))

    return (MemTotal, MemUsed, MemUsedPerc, MemAvailable,
            MemHugePagesTotal, MemHugePagesUsage, MemHugePagesUsagePerc,
            MemAnonHugePages, MemHugePageSize)

def check_swap():
    """Return Total and Used Swap in bytes and percent Utilization"""

    # example:
    #   Filename     Type         Size    Used    Priority
    #   /dev/dm-0    partition    8388604 11512   -1
    swapinfo = _readfile('/proc/swaps', abort_on_error=False, header=True)

    SwapTotal = SwapUsed = SwapUsedPerc = 0
    if swapinfo:
        for line in swapinfo:
            cols = line.rstrip().split()
            if not cols[0].startswith('/'):
                continue
            SwapTotal += int(cols[2])
            SwapUsed += int(cols[3])

        SwapUsedPerc = _perc(SwapUsed, SwapTotal)

    return (SwapTotal, SwapUsed, SwapUsedPerc)

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

def warning(message):
    "Print a warning message"
    sys.stderr.write('Warning: %s\n' % message)

def main():
    # CSVOUTPUT=1 ./syscheck.py --> Output in CSV Format
    EnvCSVOutput = os.environ.get('CSVOUTPUT', '')

    # Hostname and FQDN
    Hostname = socket.gethostname()
    FQDN = socket.getfqdn()

    # CPU utilization
    CPUMzTotal, CPUConsumption, CPUs = check_cpu()

    # Memory and Huge Memory utilization
    (MemTotal, MemUsed, MemoryUsedPerc, MemAvailable,
     MemHugePagesTotal, MemHugePagesUsage,
     MemHugePagesUsagePerc, MemAnonHugePages,
     MemHugePageSize) = check_memory()

    # Swap utilization
    SwapTotal, SwapUsed, SwapUsedPerc = check_swap()

    # System Uptime
    SystemUptime, UpDays, UpHours, UpMinutes = check_uptime()

    if EnvCSVOutput:
        print "Hostname,FQDN,CPU Total (MHz),CPU Consumption,CPUs,\
Memory Total (kB),Memory Used (%%),Mem Available (kB),\
Total Huge Pages,HugePages Usage (%%),Anonymous Huge Pages (kB),\
Total Swap (kB),Swap Usage (%%),Uptime (days)\n\
%s,%s,%d,%.2f,%d,%d,%.2f,%d,%d,%.2f,%d,%d,%.2f,%s" % (
            Hostname, FQDN, CPUMzTotal, CPUConsumption, CPUs,
            MemTotal, MemoryUsedPerc, MemAvailable,
            MemHugePagesTotal, MemHugePagesUsagePerc, MemAnonHugePages,
            SwapTotal, SwapUsedPerc, UpDays)
    else:
        print "                 Hostname : %s (%s)" % (Hostname, FQDN)
        print "             CPU Tot/Used : %s / %.2f%% (%dCPU(s))" %(
            _sizeof_fmt(CPUMzTotal, skip=2, suffix='Hz'),
            CPUConsumption, CPUs)
        print "Memory Tot/Used/Available : %s / %.2f%% / %s" % (
            _sizeof_fmt(MemTotal), MemoryUsedPerc, _sizeof_fmt(MemAvailable))
        print "      Huge Pages Tot/Used : %d / %.2f%% (HugePageSize: %s)" % (
            MemHugePagesTotal, MemHugePagesUsagePerc,
            _sizeof_fmt(MemHugePageSize))
        print "     Anonymous Huge Pages : %s" % _sizeof_fmt(MemAnonHugePages)
        print "            Swap Tot/Used : %s / %.2f%%" % (
            _sizeof_fmt(SwapTotal), SwapUsedPerc)
        print "            System uptime : %s" % SystemUptime

if __name__ == '__main__':
    exitcode = 0
    try:
        main()
    except KeyboardInterrupt:
        die(3, 'Exiting on user request')
    sys.exit(exitcode)

# vim:ts=4:sw=4:et
