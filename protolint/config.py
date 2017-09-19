# -*- coding: utf-8 -*-

"""

  protolint: config
  ~~~~~~~~~~~~~~~~~

"""

import sys
import json
import pprint

from . import output


class LinterConfig(object):

  """ Read, parse, and hold onto the linter
      configuration passed in by the runtime. """

  __slots__ = ('_config', '_filepath', '_workspace')

  def __init__(self, filepath, workspace):

    """ Initialize the linter configuration and prepare to lint
        the code specified in `workspace`, by reading the config
        file at `filepath` and parsing it as JSON.

        :param filepath: Path to the configuration file to load.
        :param workspace: Path to the code workspace to lint. """

    self._filepath = filepath
    self._workspace = workspace

    try:
      with open(filepath, 'r') as fhandle:
        self._config = json.load(fhandle)

        output.say("Parsed config: \n" + pprint.pformat(self._config, indent=2))

    except IOError as e:
      print("Encountered IOError while reading config file: %s" % e)
      sys.exit(1)

    except Exception as e:
      print("Encountered unhandled exception while reading config file: %s" % e)
      sys.exit(1)

  def __getitem__(self, item):

    """ Get a config item. """

    return self._config.get('config', {}).get(item, None)

  @property
  def config(self):

    """ Return the parsed linter configuration. """

    return self._config.get('config', {})

  @property
  def filepath(self):

    """ Return the path to the config file. """

    return self._filepath

  @property
  def workspace(self):

    """ Return the path to the code workspace. """

    return self._workspace

  @property
  def include_paths(self):

    """ Return paths to include from linting.
        :returns: Set of paths to include, or empty set. """

    if 'protopaths' in self._config.get('config', {}):
      return self._config['config']['protopaths']
    return frozenset(set(self._config.get('include_paths', tuple())).union(set((self.workspace,))))

  @property
  def exclude_paths(self):

    """ Return paths to exclude from linting.
        :returns: Set of paths to exclude, or empty set. """

    return self._config.get('exclude_paths', frozenset())

  @property
  def config_items(self):

    """ Return paths to include from config.
        :returns: Set of paths to include, or empty set. """

    return filter(lambda x: x not in frozenset(('include_paths', 'exclude_paths')),
                      self._config.get('config', {}).keys())
