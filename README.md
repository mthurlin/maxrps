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