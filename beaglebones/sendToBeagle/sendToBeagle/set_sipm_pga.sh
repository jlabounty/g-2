#!/bin/bash
if [ $# -ne 3 ]; then
    echo 'usage: set_sipm_pga [calo] [sipm] [pga]'
    exit
fi

dir=`dirname "$(readlink -f "$0")"`

b_board=`psql -h g2db-priv -U gm2_reader -d gm2_online_prod -p 5433 -c "select breakoutboard from calo_connection where calo_id=$1 and calo_xtal_num=$2;" | sed -n 3p`
board=`cut -d '-' -f1 <<< $b_board`
chan=`cut -d '-' -f2 <<< $b_board` 
python $dir/send_message.py 192.168.$1.21 board $board chan $(($chan-1)) gain $3
