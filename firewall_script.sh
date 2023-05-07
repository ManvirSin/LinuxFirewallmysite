#!/bin/bash
# firewall_script.sh

# $1 here is the first argument passed to the script, which should be the iptables rule
/sbin/iptables $1
