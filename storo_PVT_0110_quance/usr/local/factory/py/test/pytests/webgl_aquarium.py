# Copyright 2013 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""WebGL performance test that executes a set of WebGL operations."""

import time
import logging

import factory_common  # pylint: disable=unused-import
from cros.factory.test import test_case
from cros.factory.device import device_utils
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg
from cros.factory.test.pytests import thermal_load
from cros.factory.test import session

temp_result_list = []


class WebGLAquariumTest(test_case.TestCase):
  ARGS = [
      Arg('duration_secs', int, 'Duration of time in seconds to run the test',
          default=60),
    Arg('max_cpu_temp', int, 'max cpu tempreate, failed when greate than this value',
        default=90),
      Arg('hide_options', bool, 'Whether to hide the options on UI',
          default=True),
      Arg('full_screen', bool, 'Whether to go full screen mode by default',
          default=True)
  ]
  temp_result_loop = 0

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.end_time = time.time() + self.args.duration_secs

    if self.args.full_screen:
      self.ui.CallJSFunction('toggleFullScreen')
    session.console.info("max_cpu_temp : %d " % (self.args.max_cpu_temp))
    self.temp_result_loop = 0

  def FormatSeconds(self, secs):
    hours = int(secs / 3600)
    minutes = int((secs / 60) % 60)
    seconds = int(secs % 60)
    return '%02d:%02d:%02d' % (hours, minutes, seconds)

  def now_to_date(format_string="%Y-%m-%d %H:%M:%S"):
    time_stamp = int(time.time())
    time_array = time.localtime(time_stamp)
    str_date = time.strftime(format_string, time_array)
    return str_date

  def PeriodicCheck(self):
    time_left = self.end_time - time.time()
    if time_left <= 0:
      self.PassTask()
    self.ui.CallJSFunction(
        'updateUI', self.FormatSeconds(time_left),
        self.args.hide_options)

  def runTest(self):
    self.event_loop.AddTimedHandler(self.PeriodicCheck, 1, repeat=True)
    self.CheckForever()
    self.WaitTaskEnd()
  
  def Checktemp(self):
    allTemperatures = self.dut.thermal.GetAllTemperatures()
    core_key=""
    for i in range(100):
      core_key = "coretemp.0 Core %d"%i
      core_value = allTemperatures.get(core_key)
      if core_value != None:
        cpu_temp = core_value
        break
    #cpu_temp = self.dut.thermal.GetAllTemperatures()['coretemp.0 Core 0']
    temp_result_list.append(cpu_temp)
    #print(self.dut.thermal.GetAllTemperatures())
    logging.info('cpu_temp:%s [%d].', core_key, cpu_temp)
    time.sleep(2)

    temp_result_total = 0
    if len(temp_result_list)>=5:
      for temp in temp_result_list:
          temp_result_total += temp
      temp_result_ave = temp_result_total/len(temp_result_list)
      self.temp_result_loop += 1
      temp_result_list.clear()
      logging.info('temp_result_ave [%d]: %d.', self.temp_result_loop, temp_result_ave)
      session.console.info("temp_result_ave [%d]: %d " % (self.temp_result_loop, temp_result_ave))
      if temp_result_ave >= self.args.max_cpu_temp:
        self.frontend_proxy.JudgeSubTest(False)

    #self.assertTrue(cpu_temp >=90,'***Over Hot!!!***,Highest temperature allowed is 90')

  def CheckForever(self):
    while self.end_time - time.time() > 0:
      self.Checktemp()
    print("finished!!")
    return
