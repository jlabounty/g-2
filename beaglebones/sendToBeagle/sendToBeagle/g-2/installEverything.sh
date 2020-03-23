#!/bin/bash

pushd /home/g-2/setupPackages

pushd zeromq-4.2.1; ./configure; make; make install; ldconfig; popd;

cp cppzmq/zmq*hpp /usr/local/include

pushd pyzmq-15.2.0; python setup.py install; popd;

pushd setproctitle-1.1.10; python setup.py install; popd

pushd spidev-3.2; python setup.py install; popd

pushd /home/g-2/dts; dtc -O dtb -o BB-SPI0-01-00A0.dtbo -b 0 -@ BB-SPI0-01-00A0.dts; dtc -O dtb -o BB-SPI1-01-00A0.dtbo -b 0 -@ BB-SPI1-01-00A0.dts; cp *dtbo /lib/firmware; popd

pushd /home/g-2/beagle-code; make; popd

cp /home/g-2/beaglecron /etc/cron.d/beaglecron

cp /home/g-2/devrules/96-bk.rules /etc/udev/rules.d/96-bk.rules

popd

