# syscheck

A simple Python tool that displays CPU and memory utilization.

Usage:

```sh
$> ./syscheck.py
Hostname        : myserver (myserver.mydomain.com)
CPU Tot/Used    : 26887MHz/58.44% (8CPU(s))
Memory Tot/Used : 16001Mb/50.95%
Swap Tot/Used   : 8191Mb/0.14%
System uptime   : 5 days, 2:11:17.950000
```

or 

```sh
$ CSVOUTPUT=1 ./syscheck.py 
Hostname,FQDN,CPUMzTotal,CPUConsumption,CPUs,MemTotal(Mb),MemoryUsagePerc,SwapTotal(Mb),SwapUsagePerc,UptimeDays
myserver,myserver.mydomain.com,26783,58.10,8,16001,52.90,8191,0.14,5
```

The CPU utilization is calculated by looking at the kernel informations provided in `/proc/stat`.
These are amount of time that the system spent, _starting from the kernel boot_, in various states:
user mode, user mode with low priority, system mode, idle task, waiting for I/O to complete...

The file `/proc/meminfo` reports statistics about memory usage on the system and is parsed for 
reporting the memory part of the output.

