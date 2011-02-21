Introduction
========
This program tries its best to find the maximum number of requests/second a HTTP server can perform, while keeping the median latency and error percentage below user defined values.

It does so by increasing and decreasing the number of concurrent connections used until it finds a stable number. 

Usage
=====
    Usage: maxrps.py [options] url
    
    Options:
      -h, --help            show this help message and exit
      -t TIME, --time=TIME  Median latency accepted in milliseconds. Default: 250 ms
      -m MAXTIME, --maxtime=MAXTIME Maximum latency accepted (anything else will be a failed request) in milliseconds. Default: 1000 ms
      -e ERRORRATE, --errorrate=ERRORRATE Maximum accepted error rate (in percent) Default: 5
      -c CONCURRENCY, --concurrency=CONCURRENCY Number of concurrent requests to start at. Default: 1
      -q, --quiet           Do not print status updates in short intervals
      
  
Example output
==============
    python maxrps.py http://192.168.8.5 -c 30 -t 100
    
    Benchmarking http://192.168.8.5
    Starting at 30 concurrent requests
    Accepted median latency of 100 ms (maximum accepted 1000 ms)
    
    
    > RPS: 190 C: 30 Requests:     95 Errors:    0   (0.0%)   139ms   3.06 mbit/s
    
    ###############################################################################
    # RPS:  95 C: 30 Requests:     95 Errors:    0   (0.0%)   139ms   1.53 mbit/s #
    ###############################################################################
    
    Median latency too high, ramping down
    > RPS: 210 C: 29 Requests:    105 Errors:    0   (0.0%)   150ms   3.38 mbit/s
    > RPS: 258 C: 29 Requests:    129 Errors:    0   (0.0%)   112ms   4.15 mbit/s
    > RPS: 336 C: 29 Requests:    168 Errors:    0   (0.0%)    70ms   5.41 mbit/s
    
    ###############################################################################
    # RPS: 268 C: 29 Requests:    402 Errors:    0   (0.0%)   109ms   4.31 mbit/s #
    ###############################################################################
    
    Median latency too high, ramping down
    > RPS: 310 C: 27 Requests:    155 Errors:    0   (0.0%)    70ms   4.99 mbit/s
    > RPS: 304 C: 27 Requests:    152 Errors:    0   (0.0%)    88ms   4.89 mbit/s
    > RPS: 492 C: 27 Requests:    246 Errors:    0   (0.0%)    53ms   7.92 mbit/s
    > RPS: 494 C: 27 Requests:    247 Errors:    0   (0.0%)    55ms   7.95 mbit/s
    
    ###############################################################################
    # RPS: 398 C: 27 Requests:    800 Errors:    0   (0.0%)    58ms   6.41 mbit/s #
    ###############################################################################
    
    > RPS: 242 C: 27 Requests:    121 Errors:    0   (0.0%)    98ms   3.90 mbit/s
    > RPS: 416 C: 27 Requests:    208 Errors:    0   (0.0%)    65ms   6.70 mbit/s
    > RPS: 412 C: 27 Requests:    206 Errors:    0   (0.0%)    55ms   6.63 mbit/s
    > RPS: 386 C: 27 Requests:    193 Errors:    0   (0.0%)    60ms   6.21 mbit/s
    > RPS: 256 C: 27 Requests:    128 Errors:    0   (0.0%)   111ms   4.12 mbit/s
    
    ###############################################################################
    # RPS: 341 C: 27 Requests:    856 Errors:    0   (0.0%)    63ms   5.50 mbit/s #
    ###############################################################################
    
    ... etc until stopped