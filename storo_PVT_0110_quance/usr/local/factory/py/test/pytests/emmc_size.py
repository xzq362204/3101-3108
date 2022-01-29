# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test if the memory size is correctly written in the firmware.

Description
-----------
Linux kernel trusts the available memory region specified from firmware, via
ACPI or Device Tree. However, it is possible for the firmware to send wrong
values, for example always only assigning 8GB for kernel while the system
has 16GB memory installed.

On traditional PC, the memory information is stored on SPD chipset on memory
module so firmware should read and claim free space for kernel according to SPD.
On modern Chromebooks, the SPD is replaced by a pre-defined mapping table and
decided by straps. When the mapping table is out-dated, for example if an old
firmware is installed, then the allocated memory for kernel would be wrong.

The Chrome OS command, ``mosys``, can read from physical or virtual SPD and
report expected memory size. So this test tries to compare the value from
``mosys`` and kernel ``meminfo`` to figure out if firmware has reported wrong
memory size for kernel.

Usually firmware has to reserve some memory, for example ACPI tables, DMA,
I/O port mappings, so the kernel is expected to get less memory. This is
specified by argument ``max_diff_gb``.

Meanwhile, for virtual SPD, it is possible that both firmware and ``mosys`` have
out-dated information of memory straps, so optionally we support a third source,
the shopfloor backend, to provide memory size.

If argument ``device_data_key`` is set, we will also check emmc size by the
information from device data (usually retrieved from shopfloor backend if
factory supports it).

Test Procedure
--------------
This is an automated test without user interaction.

When started, the test collects memory size information from different source
and fail if the difference is too large.

Dependency
----------
- Command ``mosys``: ``mosys -k memory spd print geometry``.
- Kernel to support ``/proc/meminfo``, search for string ``MemTotal``.
- Optionally, shopfloor integration to save memory in device data.

Examples
--------
To compare and check only the memory size from ``mosys`` and kernel, add this
in test list::

  {
    "pytest_name": "memory_size"
  }

To read device data from Shopfloor Service then compare and check the memory
size from ``mosys``, kernel, and device data ``component.memory_size``, with
difference up to 300MB::

  {
    "pytest_name": "shopfloor_service",
    "args": {
      "method": "GetDeviceInfo"
    }
  }

  {
    "pytest_name": "memory_size",
    "args": {
      "device_data_key": "component.memory_size",
      "max_diff_gb": 0.3
    }
  }
"""

import re
import logging

from cros.factory.test import device_data
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.device import device_utils


class MemorySize(test_case.TestCase):
  ARGS = [
      Arg('device_data_key', str,
          'Device data key for getting emmc size in GB.',
          default=None),
      Arg('max_diff_gb', float,
          ('Maximum tolerance difference between emmc size detected by '
           'kernel and command("lsblk") in GB.'),
          default=10.0)
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()

  def runTest(self):
    self.ui.SetState(_('Checking EMMC Size...'))

    #Get EMMC Size using command 'lsblk -nbP'
    mb_emmc_byte = 0
    output_emmc_list = self._dut.CheckOutput(['lsblk', '-nbP']).strip().split('\n')
    for size in output_emmc_list:
      get_emmc_byte = re.search(r'SIZE="([0-9]+)"', size).group(1)
      mb_emmc_byte += int(get_emmc_byte)
    mb_size_gb = round((mb_emmc_byte / 1024 ** 3 ) / 2, 1)

    #Get kernel EMMC size
    kernel_emmc_kb = 0
    with open(r'/proc/partitions', 'r') as f:
      for size in list(f)[2:]:
        kernel_emmc_kb += int(size.strip().split()[2])
      kernel_emmc_gb = round((kernel_emmc_kb / 1024.0 / 1024.0) / 2, 1)
    if abs(kernel_emmc_gb - mb_size_gb) > self.args.max_diff_gb:
      self.fail('EMMC Size Check Error: read size is %.1f GB in kernel, '
                'read MB size is %.1f GB' % (kernel_emmc_gb, mb_size_gb))

    #get shopfloor EMMC size
    if not self.args.device_data_key:
      return
    sf_emmc_gb = int(re.search(r'\s*([0-9]+)\s*GB',
                           device_data.GetDeviceData(self.args.device_data_key)).group(1))
    if abs(mb_size_gb - sf_emmc_gb) > self.args.max_diff_gb:
      self.fail('EMMC size detected in the MB (%.1f GB) is different from the,'
                'shopfloor response data (%.1f GB)' % (mb_size_gb, sf_emmc_gb))
