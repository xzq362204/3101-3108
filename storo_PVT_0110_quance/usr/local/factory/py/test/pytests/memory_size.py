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

If argument ``device_data_key`` is set, we will also check memory size by the
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
from pprint import pprint

from cros.factory.test import device_data
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import process_utils
from cros.factory.device import device_utils

class MemorySize(test_case.TestCase):
  ARGS = [
      Arg('device_data_key', str,
          'Device data key for getting memory size in GB.',
          default=None),
      Arg('max_diff_gb', float,
          ('Maximum tolerance difference between memory size detected by '
           'kernel and mosys in GB.'),
          default=0.5),
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()

  def runTest(self):
    self.ui.SetState(_('Checking memory info...'))

    if not self.args.device_data_key:
      return

    sf_mem_size = re.search(r'\s*([0-9]+)\s*GB',
                         device_data.GetDeviceData(self.args.device_data_key)).group(1)
    sf_mem_gb = int(sf_mem_size)

    # Get kernel meminfo.
    with open('/proc/meminfo', 'r') as f:
      kernel_mem_kb = int(re.search(r'^MemTotal:\s*([0-9]+)\s*kB',
                                    f.read()).group(1))
    kernel_mem_gb = round(kernel_mem_kb / 1024.0 / 1024.0, 1)

    diff = abs(kernel_mem_gb - sf_mem_gb)
    if diff > self.args.max_diff_gb:
      self.fail('Memory size detected by kernel(%.1f GB) is different from device data(%.1f GB)  '
                '%.1f GB' % (kernel_mem_gb,sf_mem_gb,diff))
      return