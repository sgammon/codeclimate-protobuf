# -*- coding: utf-8 -*-

"""

  testsuite: config
  ~~~~~~~~~~~~~~~~~

"""

import unittest

import protolint
from .base import switchout_streams, restore_streams


class ConfigTests(unittest.TestCase):

  """ Test the `protolint.config` package. """

  def test_construct(self):

    """ construct a `LinterConfig` and make sure it works """

    from protolint import config
    lint = config.LinterConfig("protolint_tests/configs/sample.json", "protolint_tests/")

  def test_properties(self):

    """ construct a `LinterConfig` and make sure properties are sensible """

    from protolint import config
    lint = config.LinterConfig("protolint_tests/configs/sample.json", "protolint_tests/")
    self.assertTrue(lint != None, "linter must be constructable")
    self.assertTrue(lint.config != None, "linter must be able to load and parse config")
    self.assertEqual(lint.filepath, "protolint_tests/configs/sample.json", "linter config file path must be properly parsed")
    self.assertEqual(lint.workspace, "protolint_tests/", "workspace path must be properly parsed")


  def test_include_paths(self):

    """ construct a `LinterConfig` and make sure include paths get loaded """

    from protolint import config
    lint = config.LinterConfig("protolint_tests/configs/sample.json", "protolint_tests/")
    self.assertTrue('include_paths' in lint.config, "raw config must have include_paths")
    self.assertTrue('protos/set1' in [i for i in lint.include_paths], "raw config must have include_paths with proper entries")

  def test_config_items(self):

    """ construct a `LinterConfig` and make sure non-include-path config gets loaded """

    from protolint import config
    lint = config.LinterConfig("protolint_tests/configs/sample_with_config.json", "protolint_tests/")
    self.assertTrue('include_paths' in lint.config, "raw config must have include_paths")
    self.assertTrue('protos/set1' in [i for i in lint.include_paths], "raw config must have include_paths with proper entries")
    self.assertTrue('example' in [i for i in lint.config_items], "raw config items must expose configured property")

  def test_config_getitem(self):

    """ construct a `LinterConfig` and make sure it behaves like a dict for non-include-path config items """

    from protolint import config
    lint = config.LinterConfig("protolint_tests/configs/sample_with_config.json", "protolint_tests/")
    self.assertEqual(lint["example"], "hello", "non-include-path config items must be loadable via item interface")

  def test_config_missing(self):

    """ construct a `LinterConfig` and make sure it fails if the JSON file cannot be found """

    switchout_streams()
    with self.assertRaises(SystemExit):
      from protolint import config
      lint = config.LinterConfig("protolint_tests/configs/non_existent_config.json", "protolint_tests/")
    restore_streams()

  def test_config_invalid(self):

    """ construct a `LinterConfig` and make sure it fails if the JSON cannot be parsed """

    switchout_streams()
    with self.assertRaises(SystemExit):
      from protolint import config
      lint = config.LinterConfig("protolint_tests/configs/sample_invalid.json", "protolint_tests/")
    restore_streams()
