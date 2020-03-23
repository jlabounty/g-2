#!/bin/bash

if [[ $# < 1 ]]; then
    echo usage: sendToBeagle [ipaddr]
    exit 1
fi
year=`date -u +%F`
time=`date -u +%T`
ssh root@$1 "date --set $year; date --set $time; hwclock --systohc"
