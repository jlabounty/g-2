#!/usr/bin/python

import sys
import serial
import subprocess

def read_response(serial_port):
    response = ''
    while len(response) == 0 or response[-1] != '\n':
        new_char = serial_port.read(1)
        if new_char is '':
            return 'failed read'
        else:
            response += new_char
    return response


def main():
    SERIALS = []
    with open('/home/g-2/devrules/bk_serials.txt', 'r') as serialf:
        SERIALS = [line.strip() for line in serialf]
    if len(sys.argv) != 2:
        print 'usage: set_bk_env.py <dev_file>'
        sys.exit(0)
        
    bk = serial.Serial('/dev/' + sys.argv[1], 4800, timeout=0.5)
    bk.write('SOUR:CURR 0.008\n')
    resp = read_response(bk)
    bk.write('*IDN?\n')
    resp = read_response(bk)
    if resp[:-1] in SERIALS:      
        print('bknum=%i' % (SERIALS.index(resp[:-1]) + 1))
    else:
        ttyUSBnum = sys.argv[1].replace('ttyUSB', '')
        print('bknum=unrecognized%s' % ttyUSBnum)
    return


if __name__ == '__main__':
    main()

