# syscheck

A simple Python tool that displays CPU, swap and memory utilization on Linux.

Usage:

```sh
$> ./syscheck.py
                 Hostname : myhost (myhost.mydomain.com)
             CPU Tot/Used : 26397MHz / 57.28% (8CPU(s))
Memory Tot/Used/Available : 16001Mb / 59.18% / 6532Mb
       HugePages Tot/Used : 0 / 0.00% (HugePageSize: 2048Kb)
            AnonHugePages : 1830Mb
            Swap Tot/Used : 8191Mb / 0.00%
            System uptime : 6 days, 23:27:10.750000
```

or 

```sh
$ CSVOUTPUT=1 ./syscheck.py
Hostname,FQDN,CPUMzTotal,CPUConsumption,CPUs,MemTotal(Mb),MemoryUsedPerc,MemAvailable,HugePagesTotal,HugePagesUsagePerc,AnonHugePages(Mb),SwapTotal(Mb),SwapUsagePerc,UptimeDays
myhost,myhost.mydomain.com,26394,57.28,8,16001,59.18,6532,0,0.00,1830,8191,0.00,6
```

The CPU utilization is calculated by looking at the kernel informations provided in `/proc/stat`.
These are amount of time that the system spent, _starting from the kernel boot_, in various states:
user mode, user mode with low priority, system mode, idle task, waiting for I/O to complete...

The file `/proc/meminfo` reports statistics about memory usage on the system and is parsed for 
reporting the memory part of the output.

