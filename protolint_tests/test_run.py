# -*- coding: utf-8 -*-

"""

  testsuite: runner
  ~~~~~~~~~~~~~~~~~

"""

import unittest

import sys
import protolint
from .base import switchout_streams, restore_streams


class RunnerTests(unittest.TestCase):

  """ Test the entire `protolint` package. """

  def test_run_linter(self):

    """ test a full run of the linter """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample.json', 'protolint_tests/']
      run_tool()
    restore_streams()
