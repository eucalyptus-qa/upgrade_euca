#!/usr/bin/python2.6

import os
import re
import sys

eucaHome = os.environ.get('EUCALYPTUS', '/')
version = open(eucaHome + '/etc/eucalyptus/eucalyptus-version').read()
if version.startswith('eee-'):
    version = version[4:]
if not version.startswith('3.'):
    sys.exit(0)

lines = open(eucaHome + '/etc/eucalyptus/eucalyptus.conf').readlines()
conf = open(eucaHome + '/etc/eucalyptus/eucalyptus.conf', 'w')
for line in lines:
    if line.startswith('CLOUD_OPTS'):
        conf.write(re.sub(r'--java-home(=|\s+)\S+(\s|"|\')(.*)', r'\2\3', line.strip()) + '\n')
    else:
        conf.write(line)
conf.close()
