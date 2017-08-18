#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
'''
Project     :       Icinga/Nagios salt-minion down check
Version     :       0.2
Author      :       Will Platnick <wplatnick@gmail.com>
Summary     :       This program is an icinga/nagios plugin that is run from the salt-master to return a list of down minions
Dependency  :       Python 2.6, Linux, Icinga/Nagios

Usage :
```````
shell> python check_salt_minions.py
'''

import os
import sys
import subprocess
from optparse import OptionParser
import yaml
import re


# Command Line Parsing Arguements
cmd_parser = OptionParser(version = "0.1")
cmd_parser.add_option("-e", "--exclude", type="string", action = "store", dest = "exclude", help = "Exclude regex", metavar = "Exclude")
(cmd_options, cmd_args) = cmd_parser.parse_args()

command = [ 'salt-run', 'manage.status' ]
down_servers = ""
count_down_servers = 0
count_up_servers = 0


try:
  child = subprocess.Popen(command, stdout=subprocess.PIPE)
  output = child.communicate()[0]
except OSError, e:
  print "UNKNOWN: salt doesn't appear to be installed"
  exit(3)

yaml_out = yaml.load(output)

try:
  if not yaml_out['down'] and not yaml_out['up']:
    print "UNKNOWN: Server has no minions attached to it"
    exit(3)
except:
  print "UNKNOWN: Invalid JSON detected"
  exit(3)

try:
  for server in yaml_out['down']:
    if cmd_options.exclude:
      match = re.match(cmd_options.exclude, server)
      if match is None:
        count_down_servers += 1
        down_servers += server + "\n"
    else:
      count_down_servers += 1
      down_servers += server + "\n"
  for server in yaml_out['up']:
    count_up_servers += 1
except:
  print "OK"
  print "|up=" + str(count_up_servers) + " down=" + str(count_up_servers)
  exit(0)

if down_servers:
  if count_down_servers > 1:
    print "CRITICAL: " + str(count_down_servers) + " Servers Down\n"
  else:
    print "CRITICAL: " + str(count_down_servers) + " Server Down\n"
  print down_servers
  print "|up=" + str(count_up_servers) + " down=" + str(count_down_servers)
  exit(2)
else:
  print "OK"
  print "|up=" + str(count_up_servers) + " down=" + str(count_up_servers)
  exit(0)
