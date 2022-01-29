#!/bin/bash
# variable declaration here 
chmod 777 MT_Test_v5460_intel
mt_result=0

echo "--------------------------------------"
# [MT_Test]
# -f <Config File> ex: Default.dat
# -m <MT_Number> ex: 5, or 6
# -i <Interface> ex: 1: HID, 2: HID_LINUX, 3: I2C, 4: I2C-HID Chrome, 5:I2C Chrome, 6: Elan I2C-HID
# -d <Driver Interface> ex: 0: IOCTL, 1: sysfs
# -b <I2C bus ID>
# -a <Attribute Mode> ex: 0: (Reset Read, IRQ Read), 1: (Reset Read, IRQ Write),2: (Reset Write, IRQ Read), 3: (Reset Write, IRQ Write)
# -l <Log Direcotry Path> ex: /data/local/tmp
# -r <Result Mode> ex: 0: ASCII(Default), 1: Simple String, 2: ASCII & Simple String
echo "Running MT_Test..."
./MT_Test_v5460_intel -f Default_33f3_ST5.dat -m 6 -i 4

mt_result=$?

exit $mt_result 
