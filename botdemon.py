#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import webserver
from daemon import Daemon

class MyDaemon(Daemon):
    def run(self):
        webserver.start()

if __name__ == "__main__": 
    my_daemon = MyDaemon('/var/run/webserver.pid')

    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            print 'starting bot'
            my_daemon.start()
        elif 'stop' == sys.argv[1]:
            print 'stoping bot'
            my_daemon.stop()
        elif 'restart' == sys.argv[1]:
            print 'restarting bot'
            my_daemon.restart()
    else:
        print "Unknown command"
        sys.exit(2)
    sys.exit(0)
