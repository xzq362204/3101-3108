# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Validator for HWID DB."""

from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import bom
from cros.factory.hwid.v3 import verify_db_pattern


_BLOCKLIST_DRAM_TAG = set([
    'dram_default',
    'dram_placeholder',
    'a_fake_dram_0gb',
])
_VALIDATE_INTEGRITY_FUNCS = []


def _RegisterValidateIntegrityFunc(func):
  _VALIDATE_INTEGRITY_FUNCS.append(func)
  return func


class ValidationError(ValueError):
  """Indicates that validation of the HWID config failed."""


def ValidateChange(prev_db, db, ctx):
  """Verify that the change is valid.

  Returns:
    changed/added component information (ciq, qid, status) if available.
  """
  try:
    return verify_db_pattern.HWIDDBsPatternTest.ValidateChange(prev_db, db, ctx)
  except common.HWIDException as e:
    raise ValidationError(str(e))


@_RegisterValidateIntegrityFunc
def _ValidateDramTag(db):
  for dram_tag, dram_info in db.GetComponents('dram').items():
    if dram_tag in _BLOCKLIST_DRAM_TAG:
      continue
    try:
      ram_size = bom.RamSize(ram_size_str=dram_tag)
    except ValueError as ex:
      raise ValidationError(str(ex))

    if dram_info.values:
      info_size = int(dram_info.values['size'])
      if ram_size.byte_count != info_size << 20:  # defaults to MB
        raise ValidationError(
            '%r does not match size property %dM' % (dram_tag, info_size))


def ValidateIntegrity(db):
  for validation_func in _VALIDATE_INTEGRITY_FUNCS:
    validation_func(db)
