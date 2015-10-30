# syscheck

A simple Python tool that displays CPU, swap, memory utilization and system uptime on Linux.

Usage:

```sh
$> ./syscheck.py
                 Hostname : myhost (myhost.mydomain.com)
             CPU Tot/Used : 26.8gHz / 64.25%
         CPU Architecture : 1 socket(s) / 8 CPU(s) / 0 offline
Memory Tot/Used/Available : 15.6gB / 58.73% / 6.4gB
      Huge Pages Tot/Used : 0 / 0.00% (HugePageSize: 2.0mB)
     Anonymous Huge Pages : 2.0gB
            Swap Tot/Used : 8.0gB / 0.15%
            System uptime : 7 days, 1:37:11.830000
```

or 

```sh
$ CSVOUTPUT=1 ./syscheck.py
Hostname,FQDN,CPU Total (MHz),CPU Utilization,CPU Sockets,CPUs,Offline CPUs,Memory Total (kB),Memory Used (%),Mem Available (kB),Total Huge Pages,Huge Pages Usage (%),Anonymous Huge Pages (kB),Total Swap (kB),Swap Usage (%),Uptime (days)
myhost,myhost.mydomain.com,26723,64.25,1,8,0,16385160,58.73,6430792,0,0.00,2007040,8388604,0.15,7
```

The CPU utilization is calculated by looking at the kernel informations provided in `/proc/cpuinfo` and `/proc/stat`.
These are amount of time that the system spent, _starting from the kernel boot_, in various states:
user mode, user mode with low priority, system mode, idle task, waiting for I/O to complete...

The files `/proc/meminfo` and `/proc/swaps` are parsed for reporting the statistics about memory
and swap usage.

