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
    counter = 0
    while True:
        bk = None
        try:
            bk = serial.Serial('/dev/bkunrecognized%i' % counter, 4800, timeout=0.5)
        except:
            break
        bk.write('*IDN?\n')
        resp = read_response(bk)
        print(('%s' % resp).strip())
        counter += 1
        bk.close()


if __name__ == '__main__':
    main()

