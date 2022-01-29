# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Probes SIM card

Detects eSIM and physical SIM card by qmicli.

Args:
  tray_already_present:SIM card tray is in machine before test starts.
"""

import logging
import re

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import type_utils


_SIM_PRESENT_RE = re.compile(r'Card status: present', re.IGNORECASE)
_IS_EUICC_RE = re.compile(r'Is eUICC: yes', re.IGNORECASE)
_SUCCESS = 'Successfully got slots status'
_FibocommSuccess = 'CHECK_SIM'

_INSERT_CHECK_PERIOD_SECS = 0.5

_TrayState = type_utils.Enum(['INSERTED', 'REMOVED','UNKNOWNSTATE'])
L850_Sim_Cmd = "cd /usr/local/factory/fibocomm/L850;./FIBOCOM_MT_V1.0.0.5 -fSIM_CARD"
NL668_Sim_Cmd = "cd /usr/local/factory/fibocomm/NL668;./FIBOCOM_MT_V1.0.0 -fSIM_READY"
#Fibocomm_Sim_Cmd = ""
NL668_MOUNT_CMD = "mount /tmp -o remount,exec"
class ProbeTrayException(Exception):
  pass


class ProbeSimCardTest(test_case.TestCase):
  """Test to probe sim card.

  Number of SIM card - Number of eSIM = Number of regular sim card

  Usage examples:
    1.Just check presence or absence:
      tray_already_present=True/False
    2.Ask user to insert tray:
      tray_already_present=False,
      insert=True,
      only_check_presence=False
    3.Ask user to remove tray:
      tray_already_present=True,
      remove=True,
      only_check_presence=False
    4.Ask user to insert then remove tray:
      tray_already_present=False,
      insert=True,
      remove=True,
      only_check_presence=False
    5.Ask user to remove then insert tray:
      tray_already_present=True,
      insert=True,
      remove=True,
      only_check_presence=False
  """
  ARGS = [
      Arg('timeout_secs', int,
          'timeout in seconds for insertion/removal', default=10),
      Arg('tray_already_present', bool,
          'SIM card tray is in machine before test starts', default=False),
      Arg('insert', bool, 'Check sim card tray insertion', default=False),
      Arg('remove', bool, 'Check sim card tray removal', default=False),
      Arg('only_check_presence', bool,
          'Only checks sim card tray presence matches tray_already_present. '
          'No user interaction required', default=True),
      Arg('number_of_esim', int,
          'number of eSIM', default=0)]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.Fibocomm_Sim_Cmd = ""
  def runTest(self):
    #check  module type
    self.ui.StartFailingCountdownTimer(self.args.timeout_secs)
    self.ui.SetState(_('Detect Module Type...'))
    for loop in range(20):
        check_module_cmd = "mmcli -L"
        check_result = self.dut.CheckOutput(check_module_cmd, log=True)
        session.console.info("cmd : %s return: %s." % (check_module_cmd, check_result))
        if 'NL668' in check_result:
            mount_result = self.dut.CheckOutput(NL668_MOUNT_CMD, log=True)
            session.console.info("cmd : %s return: %s." % (NL668_MOUNT_CMD, mount_result))
            self.Fibocomm_Sim_Cmd = NL668_Sim_Cmd
            break
        elif 'L850-GL' in check_result:
            self.Fibocomm_Sim_Cmd = L850_Sim_Cmd
            break
        else:
            if loop > 18:
                self.FailTask(
                    "Unknown Module Type!")
            else:
                self.Sleep(_INSERT_CHECK_PERIOD_SECS)

    self.ui.SetState(_('Start to monitor SimCard State...'))
    session.console.info("Check sim card command:%s." % self.Fibocomm_Sim_Cmd)

    #self.CheckPresence(Fibocomm_Sim_Cmd)
    #if self.args.only_check_presence:
    #  return

    if self.GetDetection(self.Fibocomm_Sim_Cmd) == _TrayState.INSERTED:
        self.ui.SetState(_('SIM CARD Has already inserted,please remove it'))
        session.console.info("SIM CARD Has already inserted,please remove it")
        self.WaitTrayRemoved(self.Fibocomm_Sim_Cmd)
        self.ui.SetState(_('Detect SIM CARD Has already removed,waiting remove SIM CARD tray'))
        session.console.info("Detect SIM CARD Has already removed")
        #self.WaitTrayInserted(Fibocomm_Sim_Cmd)
    else:
        self.ui.SetState(_('Please insert SIM card tray'))
        self.WaitTrayInserted(self.Fibocomm_Sim_Cmd)
        self.ui.SetState(_('Detect SIM CARD Has already inserted,please remove it'))
        session.console.info("Detect SIM CARD Has already inserted,please remove it")
        self.WaitTrayRemoved(self.Fibocomm_Sim_Cmd)
        self.ui.SetState(_('Detect SIM CARD Has already removed'))
        session.console.info("Detect SIM CARD Has already removed")

  def GetDetection(self, checkcmd):
    session.console.info("Detect sim card command:%s" % (checkcmd))
    response = ""
    for loop in range(5):
        self.Sleep(_INSERT_CHECK_PERIOD_SECS)
        response = self.dut.CheckOutput(checkcmd, log=True)
        session.console.info("cmd : %s return: %s." % (checkcmd, response))
        if _FibocommSuccess not in response:
            logging.info('The original response is:\n%s' % response)
        elif 'No Response' in response:
            self.Sleep(0.5)
            logging.info('The original response is:\n%s' % response)
        else:
            break
    SimState1 = response.split(",")
    SimState = ""
    listlen = len(SimState1)
    if listlen > 2:
        SimState = SimState1[2]
    else:
        return _TrayState.REMOVED
    if SimState.upper() == "READY":
        return _TrayState.INSERTED
    else:
        return _TrayState.REMOVED

  def CheckPresence(self, cmd):
    self.assertEqual(
        self.args.tray_already_present,
        self.GetDetection(cmd) == _TrayState.INSERTED,
        ('Unexpected tray %s. Please %s SIM card tray and retest.' %
         (('absence', 'insert')
          if self.args.tray_already_present else ('presence', 'remove'))))

  def WaitTrayInserted(self, cmd):
    self.ui.SetState(_('Please insert the SIM card tray'))
    self.WaitTrayState(_TrayState.INSERTED,cmd)

  def WaitTrayRemoved(self, cmd):
    self.ui.SetState(_('Detected! Please remove the SIM card tray'))
    self.WaitTrayState(_TrayState.REMOVED, cmd)

  def WaitTrayState(self, state, cmd):
    logging.info('wait for %s event', state)

    while True:
      if self.GetDetection(cmd) == state:
        logging.info('%s detected', state)
        session.console.info('%s detected', state)
        return

