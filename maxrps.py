#!/bin/sh
import gevent
from gevent import monkey
monkey.patch_all()


import time, sys, urllib2, operator
from optparse import OptionParser


parser = OptionParser(usage="usage: %prog [options] url")
parser.add_option("-t", "--time", action="store", type="int", dest="time", default=250, help="Median latency accepted in milliseconds. Default: 250 ms")
parser.add_option("-m", "--maxtime", action="store", type="int", dest="maxtime", default=1000, help="Maximum latency accepted (anything else will be a failed request) in milliseconds. Default: 1000 ms")
parser.add_option("-e", "--errorrate", action="store", type="int", dest="errorrate", default=5, help="Maximum accepted error rate (in percent) Default: 5")
parser.add_option("-c", "--concurrency", action="store", type="int", dest="concurrency", default=1, help="Number of concurrent requests to start at. Default: 1")
parser.add_option("-q", "--quiet", action="store_true", dest="quiet", help="Do not print status updates in short intervals", default=False)

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.print_help()
    sys.exit(1)
    
url = args[0]

print
print "Benchmarking %s" % (url, )
print "Starting at %d concurrent requests" % (options.concurrency, )
print "Accepted median latency of %d ms (maximum accepted %d ms)" % (options.time, options.maxtime)
print
print



class Response:
    start = None
    end = None
    latency = None
    contentLength = None
    error = None
    
    @property
    def latency(self):
        return self.end - self.start
    

class Worker():
    def __init__(self, master):
        self.master = master
        self.responses = set()
        self.task = None
        self.keepGoing = True

    def start(self):
        self.task = gevent.spawn(self.run)
        return self

    def report(self):
        bytes = success = error = 0
        latencies = []
        for r in self.responses:
            if r.error:
                error += 1
            else:
                success += 1
                latencies.append(r.latency)
                bytes += r.contentLength
                
        self.responses.clear()
        return (success, error, latencies, bytes)
        

    def run(self):
        while self.keepGoing:
            response = Response()
            response.start = time.time()
            try:
                def performCall():
                    http = urllib2.urlopen(self.master.url)
                    return http.read()
                    
                bytes = gevent.with_timeout(self.master.maxLatency, performCall)
                response.contentLength = len(bytes)
            except BaseException, e:
                response.error = str(e)
            finally:
                response.end = time.time()                   
                self.responses.add(response)


def getReport(rps, concurrency, requests, errors, errorRate, median, mbps):
    concurrency = str(int(concurrency))
    rps = str(int(rps))
    errorRate = "(%.1f%%)"%(errorRate*100,)
    mbps = "%.2f" % mbps
    requests = str(int(requests))
    errors = str(int(errors))
    median = str(int(median*1000))
    
    return ("RPS:" + rps.rjust(4) + " C:" + concurrency.rjust(3) +" Requests:" + requests.rjust(7) +" Errors:" + errors.rjust(5) + " " + errorRate.rjust(8) + " " + median.rjust(5) + "ms " + mbps.rjust(6) + " mbit/s")
        


class MaxRps(object):
    def __init__(self, url, options):
        self.url = url
        self.maxErrorRate = options.errorrate / 100.0
        self.maxMedianLatency = options.time / 1000.0
        self.maxLatency = options.maxtime / 1000.0
        self.workers = set()
        
        self.success = self.error = self.bytes = 0
        self.latencies = []

    

    def run(self):

        ramping = [3, 6, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 125, 150, 200, 250]
        
        def ramper():
            ramptime = 1
            MAXRAMPTIME = 5
            lastTime = time.time()
            lastRps = 0
            
            hasRpsDrop = False
            rampDownStreak = 0
            stableStreak = 10000
            
            while True:
                         
                gevent.sleep(ramptime)
                
                if ramptime < MAXRAMPTIME:
                    ramptime += 0.5
                    
                rampDown = False
                rampUp = 0
                concurrency = len(self.workers)
                
                errorRate = self.error / (self.success + self.error) if self.success or self.error else 0.0
                
                currentTime = time.time()
                elapsed = currentTime - lastTime
                lastTime = currentTime
                
                rps = self.success / elapsed
                                
                latencies.extend(self.latencies)
                latencies.sort()
                if latencies:
                    median = latencies[len(latencies) // 2]
                else:
                    median = 0.0
                    
                megabit = (self.bytes * 8.0) / (1024 * 1024)
                
                report = getReport(rps, concurrency, self.success+self.error, self.error, errorRate, median, megabit/elapsed)
                print
                print "#" * (len(report) + 4)
                print "# " + report + " #"
                print "#" * (len(report) + 4)
                print                                           
                
                
                self.success = self.error = self.bytes = 0
                self.latencies = []
                
                
                if concurrency > 1 and errorRate > self.maxErrorRate:
                    print "Error rate too high, ramping down"
                    rampDown = True
                
                elif concurrency > 1 and median > self.maxMedianLatency:
                    print "Median latency too high, ramping down"
                    rampDown = True
                    
                elif rps > lastRps:
                    if hasRpsDrop:
                        rampUp = 1
                    else:
                        for ramp in ramping:
                            if ramp > concurrency:
                                rampUp = ramp - concurrency
                                break
                                
                elif rps < lastRps:
                    rampUp = 1
                    hasRpsDrop = True
    
                if rampDown:
                    rampDownStreak += 1
                    stableStreak = 0
                else:
                    rampDownStreak = 0
                    stableStreak += 1
                    
                
    
                if rampDown and self.workers:
                    for i in range(rampDownStreak):
                        if self.workers:
                            worker = self.workers.pop()
                            worker.keepGoing = False      
                                     
                if stableStreak > 2:
                    for i in range(rampUp):
                        self.workers.add(Worker(self).start())
                    
                lastRps = rps

            
        gevent.spawn(ramper)
        
        for i in range(options.concurrency):
            self.workers.add(Worker(self).start())
        
        INTERVAL = 0.5
        while True:
            try:
                gevent.sleep(INTERVAL)
                success = error = 0.0
                latencies = []
                bytes = 0
                for worker in self.workers:
                    report = worker.report()
                    (wsuccess, werror, wlatencies, wbytes) = report
                    success += wsuccess
                    error += werror
                    latencies.extend(wlatencies)
                    bytes += wbytes
                    
                latencies.sort()
                if latencies:
                    median = latencies[len(latencies) // 2]
                else:
                    median = 0.0
                    
                self.success += success
                self.error += error
                self.latencies.extend(latencies)
                self.bytes += bytes
                    
                megabit = (bytes * 8.0) / (1024 * 1024)
                
                concurrency = len(self.workers)
                errorRate = error / (success + error) if success or error else 0.0
                
                if not options.quiet:
                    print "> " + getReport(success / INTERVAL, concurrency, success+error, error, errorRate, median, megabit / INTERVAL)
                
                            
            except KeyboardInterrupt:
                return


maxrps = MaxRps(url, options)
maxrps.run()