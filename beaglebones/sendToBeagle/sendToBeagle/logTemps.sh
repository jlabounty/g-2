#!/bin/bash
#log relevant SiPM temp to file
now=$(date +"%T")
echo "$now"
python send_message_succinct.py 192.168.1.21 board 2 chan 13 temp
