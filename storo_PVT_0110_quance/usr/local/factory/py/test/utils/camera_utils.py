# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Camera utilities."""

import abc
import glob
import logging
import os
import re
import string

from cros.factory.test.utils import v4l2_utils
from cros.factory.utils import file_utils
from cros.factory.utils import process_utils

from cros.factory.external import cv2 as cv


# sysfs camera paths.
GLOB_CAMERA_PATH = '/sys/bus/usb/drivers/uvcvideo/*/video4linux/video*'
RE_CAMERA_INDEX = r'/sys/bus/usb/drivers/uvcvideo/.*/video4linux/video(\d+)'

# Paths of mock images.
_MOCK_IMAGE_PATHS = ['..', 'test', 'fixture', 'camera', 'static']

_MOCK_IMAGE_720P = 'mock_A.jpg'
_MOCK_IMAGE_VGA = 'mock_B.jpg'
_MOCK_IMAGE_QR = 'mock_QR.jpg'


class CameraError(Exception):
  """Camera device exception class."""


# TODO(menghuan): remove this dead code?
def EncodeCVImage(img, file_ext):
  """Encodes OpenCV image to common image format.

  Args:
    img: OpenCV image.
    file_ext: Image filename extension. Ex: '.bmp', '.jpg', etc.

  Returns:
    Encoded image data.
  """
  unused_retval, data = cv.imencode(file_ext, img)
  return data


def ReadImageFile(filename):
  """Reads an image file.

  Args:
    filename: Image file name.

  Returns:
    An OpenCV image.

  Raise:
    CameraError on error.
  """
  img = cv.imread(filename)
  if img is None:
    raise CameraError('Can not open image file %s' % filename)
  return img


def GetValidCameraPaths(dut):
  """Gets the valid camera paths in a device.

  Args:
    dut: a cros.factory.utils.sys_interface.SystemInterface object

  Returns:
    A list of (path, device index) pairs.

  Raise:
    CameraError if no video capture interface is found.
  """
  camera_paths = dut.Glob(GLOB_CAMERA_PATH)
  if not camera_paths:
    raise CameraError('No video capture interface found')
  camera_paths = FilterNonVideoCapture(camera_paths, dut)
  return [(path, int(re.findall(RE_CAMERA_INDEX, path)[0]))
          for path in camera_paths]


def FilterNonVideoCapture(uvc_vid_dirs, dut):
  """Filters video interface without V4L2_CAP_VIDEO_CAPTURE capability.

  Since kernel 4.16, video capture interface also creates a "metadata
  interface", which will also be r'/dev/video[0-9]+'.  To know if an interface
  is video capture or metadata interface, we need to check the device
  capability.

  Args:
    uvc_vid_dirs: list of video interface paths to filter
    dut: a cros.factory.utils.sys_interface.SystemInterface object

  Returns:
    If possible, return a filtered list of interface paths, interfaces without
    "video capture" capability will be removed.
    Otherwise, return the original list.
  """
  if len(uvc_vid_dirs) == 1:
    return uvc_vid_dirs

  if dut is None:
    logging.warning('Cannot filter interface list without DUT instance')
    return uvc_vid_dirs

  result = []
  for path in uvc_vid_dirs:
    try:
      interface_id = re.search(r'video([0-9]+)$', path).group(1)
      v4l2_capability = v4l2_utils.QueryV4L2Capability(int(interface_id))
      if v4l2_utils.IsCaptureDevice(v4l2_capability):
        result.append(path)
    except Exception:
      logging.exception('Failed to get info of video interface %s',
                        interface_id)
      raise
  return result


# TODO(yllin): Support device interface for Readers.
class CameraReaderBase(metaclass=abc.ABCMeta):
  """Abstract camera reader."""

  @abc.abstractmethod
  def EnableCamera(self, **kwargs):
    """Enables camera device.

    Raise:
      CameraError on error.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def DisableCamera(self):
    """Disabled camera device.

    Raise:
      CameraError on error.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def ReadSingleFrame(self):
    """Reads a single frame from camera device.

    Returns:
      An OpenCV image.

    Raise:
      CameraError on error.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def IsEnabled(self):
    """Checks if the camera device enabled.

    Returns:
      Boolean.
    """
    raise NotImplementedError


class CVCameraReader(CameraReaderBase):
  """Camera device reader via OpenCV V4L2 interface."""

  def __init__(self, device_index=None, dut=None):
    super(CVCameraReader, self).__init__()

    self._device_index = device_index
    if self._device_index is None:
      self._device_index = self._SearchDevice(dut)
    self._device = None

  # pylint: disable=arguments-differ
  def EnableCamera(self, resolution=None):
    """Enable camera device.

    Args:
      resolution: (width, height) tuple of capture resolution.
    """
    if self._device:
      logging.warning('Camera device is already enabled.')
      return

    self._device = cv.VideoCapture(self._device_index)
    if not self._device.isOpened():
      raise CameraError('Unable to open video capture interface')
    if resolution:
      self._device.set(cv.CAP_PROP_FRAME_WIDTH, resolution[0])
      self._device.set(cv.CAP_PROP_FRAME_HEIGHT, resolution[1])

  def DisableCamera(self):
    if self._device:
      self._device.release()
      self._device = None

  def ReadSingleFrame(self):
    if not self._device:
      raise CameraError('Try to capture image with camera disabled')
    ret, cv_img = self._device.read()
    if not ret or cv_img is None:
      raise CameraError('Error on capturing. Camera disconnected?')
    return cv_img

  def IsEnabled(self):
    return bool(self._device)

  def _SearchDevice(self, dut):
    """Looks for a camera device to use.

    Args:
      dut: a cros.factory.utils.sys_interface.SystemInterface instance.

    Returns:
      The device index found.
    """
    # Search for the camera device in sysfs. On some boards OpenCV fails to
    # determine the device index automatically.
    uvc_vid_dirs = glob.glob(GLOB_CAMERA_PATH)
    if not uvc_vid_dirs:
      raise CameraError('No video capture interface found')
    uvc_vid_dirs = FilterNonVideoCapture(uvc_vid_dirs, dut)
    if len(uvc_vid_dirs) > 1:
      raise CameraError('Multiple video capture interface found')
    return int(re.search(r'video([0-9]+)$', uvc_vid_dirs[0]).group(1))


class MockCameraReader(CameraReaderBase):
  """Mocked camera device reader."""

  def __init__(self, resolution, qr=False):
    """Constructor.

    Args:
      resolution: (width, height) tuple of capture resolution.
      qr: Whether to show QR code.
    """
    super(MockCameraReader, self).__init__()
    if qr:
      image_name = _MOCK_IMAGE_QR
    elif resolution == (1280, 720):
      image_name = _MOCK_IMAGE_720P
    else:
      image_name = _MOCK_IMAGE_VGA
    paths = _MOCK_IMAGE_PATHS[:]
    paths.append(image_name)
    self._image_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), *paths))
    self._enabled = False

  # pylint: disable=arguments-differ
  def EnableCamera(self):
    self._enabled = True

  def DisableCamera(self):
    self._enabled = False

  def ReadSingleFrame(self):
    if not self._enabled:
      raise CameraError('Try to capture image with camera disabled')
    return ReadImageFile(self._image_path)

  def IsEnabled(self):
    return self._enabled


class YavtaCameraReader(CameraReaderBase):
  """Captures image with yavta."""

  _RAW_PATH = '/tmp/yavta_output.raw'
  _BMP_PATH = '/tmp/yavta_output.bmp'

  _BRIGHTNESS_SCALE = 2.0

  def __init__(self, device_index):
    """Constructor.

    Args:
      device_index: Index of video device.
    """
    super(YavtaCameraReader, self).__init__()
    self._device_index = device_index
    self._enabled = False
    self._resolution = None
    self._postprocess = False
    self._skip = 0

  # pylint: disable=arguments-differ
  def EnableCamera(self, resolution, controls=None, postprocess=False, skip=0):
    """Enable camera device.

    Args:
      resolution: (width, height) tuple of capture resolution.
      controls: v4l2 controls.
      postprocess: Whether to enhance image.
          (Do not use this for LSC/AWB calibration)
      skip: number of frames to skip before taking the image.
    """
    self._enabled = True
    if controls is None:
      controls = []
    for ctl in controls:
      command = ['yavta', '/dev/video%d' % self._device_index, '-w', ctl]
      logging.info(' '.join(command))
      process_utils.Spawn(command, check_call=True)
    self._resolution = resolution
    self._postprocess = postprocess
    self._skip = skip

  def DisableCamera(self):
    self._enabled = False

  def GetRawImage(self, filename):
    # Remove previous captured file since yavta will accumulate the frames
    file_utils.TryUnlink(filename)

    command = ['yavta', '/dev/video%d' % self._device_index,
               '-c%d' % (self._skip + 1), '--skip', str(self._skip), '-n1',
               '-s%dx%d' % self._resolution, '-fSRGGB10', '-F%s' % filename]
    logging.info(' '.join(command))
    process_utils.Spawn(command, check_call=True)

  def ReadSingleFrame(self):
    # TODO(wnhuang): implement convertion with numpy
    raise NotImplementedError

  def IsEnabled(self):
    return self._enabled


class CameraDevice:
  """Base class for camera devices."""
  def __init__(self, dut, sn_format=None, reader=None):
    """Constructor of CameraDevice

    Args:
      dut: A DUT board object.
      sn_format: A regex string describes the camera's serial number format.
      reader: A CameraReader object, defaults to CVCameraReader()
    """
    super(CameraDevice, self).__init__()
    self._dut = dut
    self._reader = reader or CVCameraReader()
    self._sn_format = None if sn_format is None else re.compile(sn_format)

  def EnableCamera(self, **kwargs):
    """Enables camera device.

    Raise:
      CameraError on error.
    """
    return self._reader.EnableCamera(**kwargs)

  def DisableCamera(self):
    """Disabled camera device.

    Raise:
      CameraError on error.
    """
    return self._reader.DisableCamera()

  def ReadSingleFrame(self):
    """Reads a single frame from camera device.

    Returns:
      An OpenCV image.

    Raise:
      CameraError on error.
    """
    return self._reader.ReadSingleFrame()

  def IsEnabled(self):
    """Checks if the camera device enabled.

    Returns:
      Boolean.
    """
    return self._reader.IsEnabled()

  def IsValidSerialNumber(self, serial):
    """Validate the given serial number.

    Args:
      serial: A serial number string.

    Returns:
      A bool, True for validated.
    """
    if self._sn_format is None:
      assert False
      return True
    return bool(self._sn_format.match(serial))

  def GetSerialNumber(self):
    """Get the camera serial number.

    Returns:
      serial: An one-line stripped string for serial number.

    Raises:
      CameraError if retreiving SN fails.
    """
    raise NotImplementedError


class USBCameraDevice(CameraDevice):
  """System module for USB camera device."""
  def __init__(self, dut, sn_sysfs_path, sn_format=None, reader=None):
    """Initialize an instance of USBCamera

    Args:
      sn_format: A regex string describes the camera's serial number format.
      sn_sysfs_path: A string represents the SN path in sysfs.
    """
    super(USBCameraDevice, self).__init__(dut, sn_format, reader)
    self._sn_sysfs_path = sn_sysfs_path

  def GetSerialNumber(self):
    def _FilterNonPrintable(s):
      """Filter non-printable characters in serial numbers.

      It is found that some devices has non-printable ascii characters at the
      beginning of the serial number read from sysfs, so we make sure to filter
      it out here.
      """
      return ''.join(c for c in s if c in string.printable)

    try:
      serial = _FilterNonPrintable(
          self._dut.ReadSpecialFile(self._sn_sysfs_path)).rstrip()
    except IOError as e:
      raise CameraError('Fail to read %r: %r' % (self._sn_sysfs_path, e))
    if serial.find('\n') >= 0:
      raise CameraError('%r contains multi-line data: %r' %
                        (self._sn_sysfs_path, serial))
    return serial


class MIPICameraDevice(CameraDevice):
  """System module for MIPI camera device."""
  def __init__(self, dut, sn_i2c_param, sn_format=None, reader=None):
    """Initialize an instance of MIPICamera

    Args:
      sn_format: A regex string describes the camera's serial number format.
      sn_i2c_param: A dictionary represnts i2c's parameters,
          including the following keys:
          'dev_node': A string to device node path, e.g. '/dev/video0'
          'bus': An int for bus channel, e.g. 1
          'chip_addr': A int represents the chip addr, e.g. 0x37
          'data_addr': A int represents the data addr, e.g. 0x3508
          'length': An int for the requested data length in bytes, e.g. 11
    """
    super(MIPICameraDevice, self).__init__(dut, sn_format, reader)
    self._sn_i2c_param = sn_i2c_param

  def GetSerialNumber(self):
    try:
      # Power on camera so we can read from I2C
      fd = os.open(self._sn_i2c_param['dev_node'], os.O_RDWR)
      peripheral = self._dut.i2c.GetPeripheral(
          self._sn_i2c_param['bus'], self._sn_i2c_param['chip_addr'], 16)
      return peripheral.Read(self._sn_i2c_param['data_addr'],
                             self._sn_i2c_param['length'])[::-2]
    except Exception as e:
      raise CameraError('Fail to read serial number: %r' % e)
    finally:
      os.close(fd)
