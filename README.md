# syscheck

A simple Python tool that displays CPU, swap and memory utilization on Linux.

Usage:

```sh
$> ./syscheck.py
                 Hostname : myhost (myhost.mydomain.com)
             CPU Tot/Used : 25.8gHz / 53.67% (8CPU(s))
Memory Tot/Used/Available : 15.6gB / 58.73% / 6.4gB
       HugePages Tot/Used : 0 / 0.00% (HugePageSize: 2.0mB)
            AnonHugePages : 1.9gB
            Swap Tot/Used : 8.0gB / 0.00%
            System uptime : 7 days, 1:37:11.830000
```

or 

```sh
$ CSVOUTPUT=1 ./syscheck.py
Hostname,FQDN,CPU Total (MHz),CPU Consumption,CPUs,Memory Total (kB),Memory Used (%),Mem Available (kB),Total Huge Pages,HugePages Usage (%),Anonymous Huge Pages (kB),Total Swap (kB),Swap Usage (%),Uptime (days)
myhost,myhost.mydomain.com,26397,53.67,8,16385160,58.73,6762812,0,0.00,2007040,8388604,0.15,7
```

The CPU utilization is calculated by looking at the kernel informations provided in `/proc/stat`.
These are amount of time that the system spent, _starting from the kernel boot_, in various states:
user mode, user mode with low priority, system mode, idle task, waiting for I/O to complete...

The file `/proc/meminfo` reports statistics about memory usage on the system and is parsed for 
reporting the memory part of the output.

