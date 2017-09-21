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

  def test_run_linter_custom_config(self):

    """ test a full run of the linter with custom config """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_with_protopaths.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_exclusion(self):

    """ test a full run of the linter with exclusions configured """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_with_exclusion.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_empty(self):

    """ test a full run of the linter with an empty project """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_empty.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_invalid_syntax_unexpected_token(self):

    """ test a full run of the linter with an unexpected token syntax error """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_invalid_syntax.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_invalid_syntax_missing_close_bracket(self):

    """ test a full run of the linter with a missing close bracket """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_invalid_syntax2.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_unused_import(self):

    """ test a full run of the linter on an unused import """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_unused_import.json', 'protolint_tests/protos/unused_import']
      run_tool()
    restore_streams()

  def test_run_linter_duplicate_enum(self):

    """ test a full run of the linter on a duplicate enum number """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_duplicate_enum_number.json', 'protolint_tests/protos/repeated_enum_number']
      run_tool()
    restore_streams()

  def test_run_linter_enum_first_must_be_zero(self):

    """ test a full run of the linter on an enum that starts at 1 """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_enum_first_must_be_zero.json', 'protolint_tests/protos/enum_first_must_be_zero']
      run_tool()
    restore_streams()

  def test_run_linter_unrecognized_type(self):

    """ test a full run of the linter on an unrecognized type """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_unrecognized_type.json', 'protolint_tests/protos/unrecognized_type']
      run_tool()
    restore_streams()

  def test_run_linter_duplicate_field(self):

    """ test a full run of the linter on a duplicate field number """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_duplicate_field_number.json', 'protolint_tests/protos/repeated_field_number']
      run_tool()
    restore_streams()

  def test_run_linter_already_defined(self):

    """ test a full run of the linter on a field with a duplicate definition """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_already_defined.json', 'protolint_tests/protos/already_defined']
      run_tool()
    restore_streams()
