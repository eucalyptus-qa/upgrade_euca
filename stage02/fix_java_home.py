#!/usr/bin/python

from euca_qa import helper
from euca_qa import euca_except_hook
import sys

class FixJavaHome(helper.AbstractHelper):
    def run(self):
        ret = 0
        for host in self.config['hosts']:
            if host.has_role('clc') or host.has_role('sc') or host.has_role('ws'):
                ret |= host.putfile('fjh.py', 'fjh.py')
                print "Fixing Java home on " + host.ip
                ret |= host.run_command('python2.6 /root/fjh.py')
        if ret > 0:
            print "[TEST REPORT] FAILED"
        else:
            print "[TEST REPORT] SUCCESS"
        return ret

if __name__ == "__main__":
    sys.excepthook = euca_except_hook(False, True)
    stage = FixJavaHome()
    sys.exit(stage.run())
