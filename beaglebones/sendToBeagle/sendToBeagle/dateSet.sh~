#!/bin/bash

if [[ $# < 1 ]]; then
    echo usage: sendToBeagle [ipaddr]
    exit 1
fi
year=`date -u +%F`
time=`date -u +%T`
scp gm2beagle.tar.gz root@$1:/home
ssh root@$1 "date --set $year; date --set $time; hwclock --systohc; pushd /home; tar xfzv gm2beagle.tar.gz; rm gm2beagle.tar.gz; pushd g-2; ./installEverything.sh; popd; popd"
