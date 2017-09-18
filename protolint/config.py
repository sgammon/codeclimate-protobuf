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

  __config = None  # parsed config from config file
  __filepath = None  # holds the path to the file
  __workspace = None  # holds the path to the code workspace

  def __init__(self, filepath, workspace):

    """ Initialize the linter configuration and prepare to lint
        the code specified in `workspace`, by reading the config
        file at `filepath` and parsing it as JSON.

        :param filepath: Path to the configuration file to load.
        :param workspace: Path to the code workspace to lint. """

    self.__filepath = filepath
    self.__workspace = workspace

    try:
      with open(filepath, 'r') as fhandle:
        self.__config = json.load(fhandle)

        output.say("Parsed config: \n" + pprint.pformat(self.__config, indent=2))

    except IOError as e:
      print("Encountered IOError while reading config file: %s" % e)
      sys.exit(1)

    except Exception as e:
      print("Encountered unhandled exception while reading config file: %s" % e)
      sys.exit(1)

  def __getitem__(self, item):

    """ Get a config item. """

    return self.__config.get(item, None)

  @property
  def config(self):

    """ Return the parsed linter configuration. """

    return self.__config

  @property
  def filepath(self):

    """ Return the path to the config file. """

    return self.__filepath

  @property
  def workspace(self):

    """ Return the path to the code workspace. """

    return self.__workspace

  @property
  def include_paths(self):

    """ Return paths to include from config.
        :returns: Set of paths to include, or empty set. """

    if 'protopaths' in self.__config.get('config', {}):
      return self.__config['config']['protopaths']
    return self.__config.get('include_paths', frozenset())

  @property
  def config_items(self):

    """ Return paths to include from config.
        :returns: Set of paths to include, or empty set. """

    return filter(lambda x: x != 'include_paths', self.__config.keys())
