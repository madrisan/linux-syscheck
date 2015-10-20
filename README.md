# syscheck

A simple Python tool that displays CPU, swap and memory utilization on Linux.

Usage:

```sh
$> ./syscheck.py
          Hostname : myserver (myserver.mydomain.com)
      CPU Tot/Used : 26783MHz/36.41% (8CPU(s))
   Memory Tot/Used : 16001Mb/50.23%
HugePages Tot/Used : 0/0.00% (HugePageSize: 2048Kb)
     AnonHugePages : 1686Mb
     Swap Tot/Used : 8191Mb/0.14%
     System uptime : 4 days, 2:36:17.450000
```

or 

```sh
$ CSVOUTPUT=1 ./syscheck.py 
Hostname,FQDN,CPUMzTotal,CPUConsumption,CPUs,MemTotal(Mb),MemoryUsagePerc,HugePagesTotal,HugePagesUsagePerc,AnonHugePages(Mb),SwapTotal(Mb),SwapUsagePerc,UptimeDays
myserver,myserver.mydomain.com,26783,36.41,8,16001,50.23,0,0.00,1686,8191,0.14,4
```

The CPU utilization is calculated by looking at the kernel informations provided in `/proc/stat`.
These are amount of time that the system spent, _starting from the kernel boot_, in various states:
user mode, user mode with low priority, system mode, idle task, waiting for I/O to complete...

The file `/proc/meminfo` reports statistics about memory usage on the system and is parsed for 
reporting the memory part of the output.

