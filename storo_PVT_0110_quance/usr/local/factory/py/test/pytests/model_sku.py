# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A test to confirm and set SKU information.

Description
-----------
A test to confirm SKU information, then apply SKU or model specific settings.
And there are two modes:

1. manually ask to operator to confirm SKU information.
2. automatically compare SKU information with device data - component.sku.

If device data - component.sku is set then this test will go to automatic mode
or manual mode will be executed.

This is a test to verify hardware root of trust, so there's no options to
set auto verification for this test. Instead, either it relies on the operator
to check manually or compares with device data from shopfloor which would need
to be configured in advance.

After the SKU is confirmed, the test will load a JSON configuration specified by
``config_name``. The config should be a dictionary containing what device data
(usually ``component.*``) to set for matched model and SKU. For example, to set
if the touchscreen is available for model 'coral' with default True, and only
False for product_name `Coral` SKU 3::

  {
    "model": {
      "coral": {
        "component.has_touchscreen": true
      }
    },
    "product_sku": {
      "Coral": {
        "3": {
          "component.has_touchscreen": false
        }
      }
    }
  }

Test Procedure
--------------
The test runs following commands:

- cros_config / name
- cros_config /identity sku-id
- cros_config / brand-code

And then asks OP to press ENTER/ESC to confirm if these values are correct.

Dependency
----------
- ``mosys`` utility.

Examples
--------
To ask OP to confirm sku information, add this in test list::

  {
    "pytest_name": "model_sku"
  }
"""

import logging
import os

from cros.factory.device import device_utils
from cros.factory.gooftool import cros_config as cros_config_module
from cros.factory.test import device_data
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test import ui_templates
from cros.factory.test.i18n import _
from cros.factory.test.utils import model_sku_utils
from cros.factory.utils.arg_utils import Arg


_KEY_COMPONENT_SKU = device_data.JoinKeys(device_data.KEY_COMPONENT, 'sku')

_PLATFORM_DATA = ['model', 'sku', 'brand']


class PlatformSKUModelTest(test_case.TestCase):
  """A test to confirm and set SKU and model information."""

  ARGS = [
      Arg(
          'config_name', str,
          'Name of JSON config to load for setting device data. Set this '
          'argument to %s if you want to load boxster data.' %
          model_sku_utils.BOXSTER, default=None),
      Arg('schema_name', str,
          'Name of JSON schema to load for setting device data.', default=None),
      Arg(
          'product_name', str,
          'The product_name of the device. If not specified, read from '
          '%s on x86 devices and %s on ARM devices.' %
          (model_sku_utils.PRODUCT_NAME_PATH,
           model_sku_utils.DEVICE_TREE_COMPATIBLE_PATH), default=None),
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._platform = {}
    self._goofy_rpc = state.GetInstance()

  def ApplyConfig(self):
    if self.args.config_name is None:
      config_name = os.path.splitext(os.path.basename(__file__))[0]
    else:
      config_name = self.args.config_name
    model_config = model_sku_utils.GetDesignConfig(
        self._dut, default_config_dirs=os.path.dirname(__file__),
        product_name=self.args.product_name, sku_id=self._platform['sku'],
        config_name=config_name, schema_name=self.args.schema_name)
    if model_config:
      logging.info('Apply model/SKU config: %r', model_config)
      device_data.UpdateDeviceData(model_config)
      # Device data might affect which tests are skipped/waived. Reload the test
      # list to correctly identify those tests.
      self._goofy_rpc.ReloadTestList()

  def CheckByOperator(self):
    self.ui.SetInstruction(_('Please confirm following values'))

    table = ui_templates.Table(
        rows=len(_PLATFORM_DATA) + 1, cols=2, element_id='mosys_table')
    table.SetContent(0, 0, '<strong>Key</strong>')
    table.SetContent(0, 1, '<strong>Value</strong>')
    for i, arg in enumerate(_PLATFORM_DATA, 1):
      table.SetContent(i, 0, arg)
      table.SetContent(
          i, 1,
          self._platform[arg] if self._platform[arg] is not None else 'N/A')

    self.ui.SetState([table.GenerateHTML(), test_ui.PASS_FAIL_KEY_LABEL])

    key = self.ui.WaitKeysOnce([test_ui.ENTER_KEY, test_ui.ESCAPE_KEY])
    if key == test_ui.ESCAPE_KEY:
      self.FailTask('Failed by operator')
    self.ApplyConfig()

  def CheckByDeviceData(self):
    value = device_data.GetDeviceData(_KEY_COMPONENT_SKU)
    if value is None:
      return False

    self.assertEqual(
        str(value), self._platform['sku'],
        'Value [%s] from "cros_config /identity sku-id" does not match '
        'device data [%s]' % (self._platform['sku'], value))

    self.ApplyConfig()
    return True

  def GetPlatformData(self):
    cros_config = cros_config_module.CrosConfig(dut=self._dut)
    self._platform['model'] = cros_config.GetModelName()
    self._platform['sku'] = cros_config.GetSkuID()
    self._platform['brand'] = cros_config.GetBrandCode()

  def runTest(self):
    self.GetPlatformData()

    if self.CheckByDeviceData():
      return

    self.CheckByOperator()
