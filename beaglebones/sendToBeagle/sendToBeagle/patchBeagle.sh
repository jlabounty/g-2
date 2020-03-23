#!/bin/bash

if [[ $# < 1 ]]; then
    echo usage: sendToBeagle [ipaddr]
    exit 1
fi
year=`date -u +%F`
time=`date -u +%T`
scp g-2/beagle-code/src/beagle_broker.cxx root@$1:/home/g-2/beagle-code/src/beagle_broker.cxx
scp g-2/beagle-code/sipmspi.py root@$1:/home/g-2/beagle-code/sipmspi.py
scp g-2/beagle-code/spiworker.py root@$1:/home/g-2/beagle-code/spiworker.py
scp g-2/beagle-code/testRequest.py root@$1:/home/g-2/beagle-code/testRequest.py
scp g-2/beaglecron root@$1:/etc/cron.d/beaglecron
scp g-2/beagle-code/bkworker.py root@$1:/home/g-2/beagle-code/bkworker.py
scp g-2/beagle-code/jmuworker.py root@$1:/home/g-2/beagle-code/jmuworker.py
scp g-2/beagle-code/startMasterWorkers.sh root@$1:/home/g-2/beagle-code/startMasterWorkers.sh
scp g-2/devrules/set_bk_env.py root@$1:/home/g-2/devrules/set_bk_env.py
ssh root@$1 "date --set $year; date --set $time; hwclock --systohc; chmod u+x /home/g-2/devrules/set_bk_env.py; cd /home/g-2/beagle-code; touch src/*; make"
