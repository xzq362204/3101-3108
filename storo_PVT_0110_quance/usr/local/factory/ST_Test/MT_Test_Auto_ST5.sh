#!/bin/bash

# Copyright 2019 Compal. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e
umask 022
# cd i2chid_read_fwid
elan_fw=`./elan_i2chid_read_fwid -s chrome -f fwid_mapping_table_new.txt`

if [ -n "$elan_fw" ]; then
    elan_fw_dir=`echo $elan_fw |awk -F 'FWID' '{print $2}' |awk -F' ' '{print $2}' |head -c 4`
else
    echo "read empty"
    exit 1
fi

if [ "$elan_fw_dir" = "360e" ]; then
    cmd="./MT_Test_360e_ST5.sh"
    $cmd
elif [ "$elan_fw_dir" = "33f3" ]; then
    cmd="./MT_Test_33f3_ST5.sh"
    $cmd
else
    echo "unknown fw"
    exit 2
fi
