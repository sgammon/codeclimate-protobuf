# -*- coding: utf-8 -*-

"""

  protolint: linter
  ~~~~~~~~~~~~~~~~~

"""

import os, sys, json, subprocess, hashlib

from . import output
from enum import Enum

try:
  import cStringIO as StringIO
except ImportError:
  import StringIO


class Linter(object):

  """ Driver object for `protoc` with `protoc-gen-lint`. """

  class Warnings(Enum):

    """ Enumerated warnings from the linter. """

    messageCase = 1  # 'Use CamelCase (with an initial capital) for message names.'
    fieldCase = 2  # 'Use underscore_separated_names for field names.'
    enumTypeCase = 3  # 'Use CamelCase (with an initial capital) for enum type names.'
    enumValueCase = 4  # 'Use CAPITALS_WITH_UNDERSCORES  for enum value names.'
    serviceCase = 5  # 'Use CamelCase (with an initial capital) for service names.'
    rpcMethodCase = 6  # 'Use CamelCase (with an initial capital) for RPC method names.'

  Names = {
    Warnings.messageCase: "Convention/Message Name Case",
    Warnings.enumTypeCase: "Convention/Enum Type Case",
    Warnings.serviceCase: "Convention/Service Name Case",
    Warnings.fieldCase: "Convention/Field Name Case",
    Warnings.enumValueCase: "Convention/Enum Value Case",
    Warnings.rpcMethodCase: "Convention/RPC Method Case"
  }

  Severity = {
    Warnings.messageCase: "major",
    Warnings.enumTypeCase: "major",
    Warnings.serviceCase: "major",
    Warnings.fieldCase: "minor",
    Warnings.enumValueCase: "minor",
    Warnings.rpcMethodCase: "minor",
  }

  SeverityHandler = {
    "major": output.error,
    "minor": output.warn
  }

  Remediation = {
    Warnings.messageCase: 50000,
    Warnings.enumTypeCase: 50000,
    Warnings.serviceCase: 50000,
    Warnings.fieldCase: 50000,
    Warnings.enumValueCase: 50000,
    Warnings.rpcMethodCase: 50000
  }

  Categories = {
    Warnings.messageCase: ["Compatibility", "Style"],
    Warnings.enumTypeCase: ["Compatibility", "Style"],
    Warnings.serviceCase: ["Compatibility", "Style"],
    Warnings.fieldCase: ["Compatibility", "Style"],
    Warnings.enumValueCase: ["Compatibility", "Style"],
    Warnings.rpcMethodCase: ["Compatibility", "Style"]
  }

  Message = {
    Warnings.messageCase: "Use CamelCase (with an initial capital) for message names.",
    Warnings.enumTypeCase: "Use underscore_separated_names for field names.",
    Warnings.serviceCase: "Use CamelCase (with an initial capital) for enum type names.",
    Warnings.fieldCase: "Use CAPITALS_WITH_UNDERSCORES  for enum value names.",
    Warnings.enumValueCase: "Use CamelCase (with an initial capital) for service names.",
    Warnings.rpcMethodCase: "Use CamelCase (with an initial capital) for RPC method names."
  }

  ## -- Internals -- ##
  __config = None  # config for the linter, parsed from JSON
  __workspace = None  # reference to the folder for the workspace
  __raw_output = None  # raw output from `protoc-gen-lint`
  __issues = None  # issues detected during the lint process
  __exit = 0  # exit code to use when done
  __arguments = None  # arguments from the CLI

  def __init__(self, config, arguments):

    """ Initialize the main `Linter` object.

        :param config: `config.LinterConfig` object. """

    self.__config = config
    self.__issues = []
    self.__arguments = arguments

  def __make_abspath(self, path):

    """ Make a path an absolute path if it isn't one already.

        :param path: Path to make absolute.
        :returns: Absolute path. """

    if path == self.config.workspace:
      return os.path.abspath(self.config.workspace)
    if not path.startswith("/"):
      return os.path.abspath(os.path.join(self.__make_abspath(self.config.workspace), path))
    return path  # already absolute

  def __scan(self, path):

    """ Scan one of the prefix paths for protos. """

    resolved_path = None
    if path.startswith('/'):
      resolved_path = path  # it's already an absolute path
    else:
      # it's relative to the workspace directory
      resolved_path = os.path.abspath(
        os.path.join(self.config.workspace, path))


    find_output = subprocess.check_output(
      ['find', resolved_path, '-name', '*.proto'])

    if find_output:
      for line in find_output.split('\n'):
        yield line.strip()

  def __command(self, base):

    """ Generate command flags to pass to `protoc`.
        
        :param base: Initial command arguments.
        :return: Command flags, based on config. """

    prefixes = []
    protofiles = []

    for configured_path in self.config.include_paths:
      include_path = self.__make_abspath(configured_path)

      if os.path.isdir(include_path):
        prefixes.append('--proto_path=%s' % include_path)

        output.say('Scanning include_path "%s"...' % include_path)

        before = len(protofiles)

        for protofile in self.__scan(include_path):
          if protofile:
            protofiles.append(protofile)

        if __debug__:
          after = len(protofiles)
          output.say('Found %s protos:' % str(after - before))
          for proto_file in protofiles:
            output.say('- %s' % proto_file)

    base.extend(prefixes)
    base.extend(protofiles)
    base.append('--lint_out=/.linter')
    return base

  def __resolve(self, issue_msg):

    """ Resolve a unique enumerated code for this issue so
        it may be understood for severity and remediation.

        :param issue_msg: Parsed message from the issue.
        :returns: Enumerated type for this issue. """

    # @TODO(sgammon): fork/file PRs to get issue ID output from plugin
    # from: https://github.com/ckaznocha/protoc-gen-lint/blob/master/linter/linter.go#L32

    if 'message names' in issue_msg:
      return Linter.Warnings.messageCase
    elif 'field names' in issue_msg:
      return Linter.Warnings.fieldCase
    elif 'enum type names' in issue_msg:
      return Linter.Warnings.enumTypeCase
    elif 'enum value names' in issue_msg:
      return Linter.Warnings.enumValueCase
    elif 'service names' in issue_msg:
      return Linter.Warnings.serviceCase
    elif 'method names' in issue_msg:
      return Linter.Warnings.rpcMethodCase
    else:
      raise ValueError('cannot parse issue line for type: %s' % issue_msg)

  def __parse(self, issue_output):

    """ Parse the output of the `protoc-gen-lint` tool.

        :param output: Output from the linter. """

    # samples:
    # TestMessageProto3.proto:19:9: 'sampleLameMessageTitle' - Use CamelCase (with an initial capital) for message names.
    # TestMessageProto3.proto:25:10: 'aggravatingCamelCase' - Use underscore_separated_names for field names.
    # TestMessageProto3.proto:14:3: 'hello' - Use CAPITALS_WITH_UNDERSCORES  for enum value names.
    for raw_issue in issue_output:
      # @TODO(sgammon): all of this parsing code needs cleanup work
      issue_split = raw_issue.split(' - ')
      assert len(issue_split) == 2, "issue split by ' - ' result was not 2: '%s'" % raw_issue
      issue_context_raw, issue_message = tuple(issue_split)

      # parse issue context
      issue_context_split = issue_context_raw.split(' ')
      issue_file_line_context, further_context = issue_context_split[0], ' '.join(issue_context_split[1:]).strip().replace('\'', '')

      # parse file/line context
      issue_file_line_context_split = issue_file_line_context.split('.proto')
      issue_file_name = '.'.join((issue_file_line_context_split[0], 'proto'))
      issue_line_number = issue_file_line_context.split(':')[1]
      issue_column_number = issue_file_line_context.split(':')[2]

      yield Issue(
        raw=raw_issue,
        type=self.__resolve(issue_message),
        message=issue_message,
        protofile=issue_file_name,
        protoline=int(issue_line_number.replace(':', '').strip()),
        protocolumn=int(issue_column_number.replace(':', '').strip()),
        protocontext=further_context)

  def __execute(self):

    """ Execute the linter tool according to the provided config,
        and gather the output so it may be parsed.

        :returns: Gathered output of the tool, in a `StringIO` object. """

    command = self.__command(['protoc'])
    issues_to_output = []
    issue_count_from_plugin = None

    try:
      result = subprocess.check_output(' '.join(command), stderr=subprocess.STDOUT, shell=True)
      
    except subprocess.CalledProcessError as e:
      if e.output:
        # we have output
        for line in e.output.split('\n'):
          # filter out lines that are empty
          if not line: continue

          # process final line
          if '--lint_out: protoc-gen-lint: Plugin failed' in line:
            # parse number of reported issues from following format:
            # '--lint_out: protoc-gen-lint: Plugin failed with status code 3.'            
            try:
              lastline_split = line.split(' ')
              count_str = lastline_split[-1].replace('.', '').strip()
              issue_count_from_plugin = int(count_str)
            except ValueError as e:
              pass

          # process issues
          else:
            # it's a warning line, due to be parsed
            issues_to_output.append(line)
      else:
        output.error("Protoc crashed but we got no output.")
        sys.exit(1)

    else:
      output.info('No issues found.')

    if (len(issues_to_output) != issue_count_from_plugin) and __debug__:
      output.warn('Number of reported issues from plugin (%s) does not match number of issues parsed (%s).' % (
        issue_count_from_plugin, len(issues_to_output)))
    else:
      output.info('Reporting %s issues.' % len(issues_to_output))

    return issues_to_output


  ## -- Properties -- ##
  @property
  def config(self):

    """ Return the active config for this linter.
        :returns: `config.LinterConfig` for this linter. """

    return self.__config

  @property
  def workspace(self):

    """ Returns the workspace being scanned.
        :returns: Current workspace. """

    return self.__workspace

  @property
  def raw_output(self):

    """ Returns the raw output from the linter tool.
        :returns: Raw, unparsed output. """

    return self.__raw_output

  @property
  def exit_code(self):

    """ Returns the exit code to use when exiting.
        :returns: Unix-like exit code. Defaults to `0`. """

    for issue in self.__issues:
      yield output.issue(issue)

  @property
  def issues(self):

    """ Yields issues detected during the linter process.
        :returns: Yields formatted issue lines one at a time. """

    for issue in self.__issues:
      yield output.issue(issue)

  ## -- CLI Interface -- ##
  def __call__(self):

    """ Run the linter tool on the configured workspace and with the
        specified config arguments, if any.

        :returns: Output code, `0` if successful, `1` if something crashed. """

    # execute protoc with protoc-gen-lint, then parse the output
    for issue in self.__parse(self.__execute()):
      self.__issues.append(issue)
      yield issue

      if hasattr(self.__arguments, 'verbose') and self.__arguments.verbose:
        output.say('Reporting issue: %s' % issue)

    raise StopIteration()


class Issue(object):

  """ Represents a detected issue by `protoc-gen-lint` that has been parsed
      from the plugin output and now provided here. """

  ## -- Internals -- ##
  __raw = None  # raw output for this issue
  __type = None  # parsed type of this issue
  __message = None  # message that was emitted
  __protofile = None  # protobuf file that caused the issue
  __protoline = None  # line in protobuf file that caused the issue
  __protocolumn = None  # column in the line in the protobuf file
  __protocontext = None  # extra context for the issue offered by the plugin

  def __init__(self, raw, type, message, protofile, protoline, protocolumn, protocontext):

    """ Initialize a detected issue from the `protoc-gen-lint` tool.

        :param raw: Raw line as emitted by the tool.
        :param code: Numeric code corresponding to this issue type.
        :param message: Message emitted by the tool, parsed from `raw`.
        :param protofile: Protobuf file that caused the issue.
        :param protoline: Line in the protobuf file that caused the issue. """

    self.__type = type
    self.__raw = raw
    self.__message = message
    self.__protofile = protofile
    self.__protoline = protoline
    self.__protocolumn = protocolumn
    self.__protocontext = protocontext

  def __repr__(self):

    """ Generate a string representation of this object. """

    return "Issue(location=%s:%s:%s, context='%s', message='%s')" % (
      self.__protofile,
      self.__protoline,
      self.__protocolumn,
      self.__protocontext,
      self.__message)

  ## -- Properties -- ##
  @property
  def type(self):

    """ Return the type of this issue.
        :returns: `linter.Linter.Warnings` type for this issue. """

    return self.__type

  @property
  def raw(self):

    """ Return the raw, unparsed line emitted by `protoc-gen-lint` for this issue.
        :returns: Raw output line. """

    return self.__message

  @property
  def message(self):

    """ Return the message emitted by `protoc-gen-lint` for this issue.
        :returns: Parsed message. """

    return self.__message

  @property
  def file(self):

    """ Return the protobuf file that caused this issue.
        :returns: Protobuf filepath and name, as returned by `protoc-gen-lint`. """

    return self.__protofile

  @property
  def line(self):

    """ Return the line in the protobuf file that caused this issue.
        :returns: Protobuf line as parsed from the filepath returned by `protoc-gen-lint`. """

    return self.__protoline

  @property
  def column(self):

    """ Return the column in the protobuf line that caused this issue.
        :returns: Protobuf column as parsed from the line returned by `protoc-gen-lint`. """

    return self.__protocolumn

  @property
  def context(self):

    """ Return the extra context offered by `protoc-gen-lint`.
        :returns: Context value as parsed from the line returned by `protoc-gen-lint`. """

    return self.__protocontext

  @property
  def unique_hash(self):

    """ Calculate and return a unique hash for this issue.
        :returns: Unique hash, as a hex digest, for this specific issue. """

    return hashlib.sha256('::'.join((map(unicode, (
      "v1",
      self.__type.name,
      self.__message,
      self.__protofile,
      self.__protoline,
      self.__protocolumn,
      self.__protocontext))))).hexdigest()

  @classmethod
  def serialize(self, exported):

    """ Serialize the exported version of this structure for use with CodeClimate.
        :returns: JSON-serialized exported object. """

    return json.dumps(exported)

  def export(self):

    """ Export this object to a dictionary that describes it so it may be written
        to `stdout` to be handled by CodeClimate.

        :returns: Exported `dict` to pass to CodeClimate. """

    return {
      "type": "issue",
      "check_name": Linter.Names[self.__type],
      "description": Linter.Message[self.__type],
      "categories": Linter.Categories[self.__type],
      "severity": Linter.Severity[self.__type],
      "fingerprint": self.unique_hash,
      "location": {
        "path": self.__protofile,
        "lines": {
          "begin": {
            "line": self.__protoline,
            "column": self.__protocolumn
          }
        }
      }
    }

  def write(self):

    """ Write this issue to `stdout` in a JSON-serialized structure
        that CodeClimate is capable of reading. """

    output.say('Writing issue "%s"...' % repr(self))
    Linter.SeverityHandler[Linter.Severity[self.__type]]("[%s]: %s" % (self.__type.name, self.__message))
    output.issue(self)

  def __call__(self):

    """ Dispatch `Issue.serialize` on the exported form of this object, which prepares
        it to be pulled into CodeClimate.

        :returns: Exported and serialized version of this issue. """

    return Issue.serialize(self.export())
