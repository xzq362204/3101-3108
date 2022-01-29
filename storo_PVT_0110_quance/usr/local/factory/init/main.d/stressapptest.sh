#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# If stressapptest64 exists, we want to use 64-bit version of stressapptest for
# memory testing. Otherwise it may hit issues if the memory size is larger than
# 4G.
# Issues: http://b/169216148, http://b/175255825

stressapptest_bin="$(which stressapptest)"
if [ -x "${stressapptest_bin}64" ]; then
  mount --bind "${stressapptest_bin}64" "${stressapptest_bin}"
fi
