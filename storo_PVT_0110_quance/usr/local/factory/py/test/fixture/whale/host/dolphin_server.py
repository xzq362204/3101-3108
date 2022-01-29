#!/usr/bin/env python3
# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""RPCServer to support serial connection to Plankton-Raiden of Dolphin."""

import argparse
import logging
import os
import subprocess
import sys
import time
import xmlrpc.server

from cros.factory.test.fixture.whale import serial_server

# server address
DEFAULT_PORT = 9997
DEFAULT_HOST = 'localhost'
DEFAULT_BOARD = 'whale_samus'

# definition of plankton raiden parameters
PLANKTON_SERIAL_PARAMS = {'driver': 'ftdi_sio',
                          'baudrate': 115200,
                          'bytesize': 8,
                          'parity': 'N',
                          'stopbits': 1,
                          'timeout': 3,
                          'writeTimeout': 3}

PLANKTON_CONN_PORT = {'whale_samus': ['1-1.3.2',  # left raiden
                                      '1-1.2.4'],  # right raiden
                      'whale_ryu': ['1-1.4']}  # right raiden


def ParseArgs():
  """Parses commandline arguments.

  Returns:
    args from argparse.parse_args().
  """
  description = (
      'A server for Dolphin serial control. '
      'This server communicates with the client via xmlrpc.'
  )

  examples = (
      '\nExamples:\n'
      '   > dolphin_server.py -p 8888\n\tLaunch server listening on port 8888\n'
  )

  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter, description=description,
      epilog=examples)
  parser.add_argument('-d', '--debug', action='store_true', default=False,
                      help='enable debug messages')
  parser.add_argument('--host', default=DEFAULT_HOST, type=str,
                      help='hostname to start server on')
  parser.add_argument('--port', default=DEFAULT_PORT, type=int,
                      help='port for server to listen on')
  parser.add_argument('--board', default=DEFAULT_BOARD, type=str,
                      help='board name for whale server')
  return parser.parse_args()


def ModprobeFtdiDriver():
  """Modprobe FTDI driver on Plankton-Raiden manually."""
  subprocess.call(['modprobe', 'ftdi_sio'])
  with open('/sys/bus/usb-serial/drivers/ftdi_sio/new_id', 'w') as f:
    f.write('18d1 500c\n')
  time.sleep(1)  # Wait after modprobe for TTY connection


def GetDolphinParamsByBoard(board):
  """Gets dolphin parameters for specified whale board name.

  Args:
    board: Board name for whale server.

  Returns:
    Dolphin parameters in a list to indicate the dolphin server(s).
  """
  if board not in PLANKTON_CONN_PORT:
    logging.info(
        'board=%s not supported, use whale_samus as default board...', board)
    board = 'whale_samus'
  logging.info('Set config board=%s', board)
  return [{'serial_params': PLANKTON_SERIAL_PARAMS,
           'port_index': port} for port in PLANKTON_CONN_PORT[board]]


def RealMain():
  args = ParseArgs()
  log_level = logging.INFO
  log_format = '%(asctime)s - %(name)s - %(levelname)s'
  if args.debug:
    log_level = logging.DEBUG
    log_format += ' - %(filename)s:%(lineno)d:%(funcName)s'
  log_format += ' - %(message)s'
  logging.basicConfig(level=log_level, format=log_format)

  logger = logging.getLogger(os.path.basename(sys.argv[0]))
  logger.info('Start')

  server = xmlrpc.server.SimpleXMLRPCServer(
      (args.host, args.port),
      allow_none=True)

  ModprobeFtdiDriver()
  dolphin_params = GetDolphinParamsByBoard(args.board)
  dolphin_server = serial_server.SerialServer(dolphin_params,
                                              verbose=args.debug)
  server.register_introspection_functions()
  server.register_instance(dolphin_server)
  logger.info('Listening on %s port %s', args.host, args.port)
  server.serve_forever()


def main():
  """Main function wrapper to catch exceptions properly."""
  try:
    RealMain()
  except KeyboardInterrupt:
    sys.exit(0)
  except serial_server.SerialServerError as e:
    sys.stderr.write('Error: ' + str(e))
    sys.exit(1)


if __name__ == '__main__':
  main()
