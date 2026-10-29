#!/bin/sh
# Name: Tableau de bord T2 - Test
# Author: Oliv
# DontUseFBInk
mkdir -p /mnt/us/dashboard/logs
exec sh /mnt/us/dashboard/dash.sh once >>/mnt/us/dashboard/logs/test.log 2>&1
