# -*- coding: utf-8 -*-

"""

  protolint: linter
  ~~~~~~~~~~~~~~~~~

"""

import os, re, sys, json, subprocess, hashlib

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
    enumValueCase = 4  # 'Use CAPITALS_WITH_UNDERSCORES for enum value names.'
    serviceCase = 5  # 'Use CamelCase (with an initial capital) for service names.'
    rpcMethodCase = 6  # 'Use CamelCase (with an initial capital) for RPC method names.'

  class Errors(Enum):

    """ Enumerated errors from the compiler. """

    fileNotFound = 7  # 'base/TestMessage.proto: File not found.'
    importUnresolved = 8  # 'invalid_import/sample/Sample.proto: Import "base/TestMessage.proto" was not found or had errors.'
    notDefined = 9  # 'invalid_import/sample/Sample.proto:13:3: "testMessage" is not defined.'
    missingFieldNumber = 10  # 'set2/TestMessage2Proto2.proto:10:37: Missing field number.'
    unexpectedToken = 11  # 'TotallyBorked.proto:9:3: Expected ";".'
    unexpectedEnd = 12  # 'TotallyBorked.proto:10:1: Reached end of input in message definition (missing '}').'

  Names = {
    # -- Warnings
    Warnings.messageCase: "Style/Message Name Case",
    Warnings.enumTypeCase: "Style/Enum Type Case",
    Warnings.serviceCase: "Style/Service Name Case",
    Warnings.fieldCase: "Style/Field Name Case",
    Warnings.enumValueCase: "Style/Enum Value Case",
    Warnings.rpcMethodCase: "Style/RPC Method Case",

    # -- Errors
    Errors.fileNotFound: "Bug Risk/File Not Found",
    Errors.importUnresolved: "Bug Risk/Import Unresolved",
    Errors.notDefined: "Bug Risk/Symbol Undefined",
    Errors.missingFieldNumber: "Bug Risk/Missing Field Number",
    Errors.unexpectedToken: "Bug Risk/Unexpected Token",
    Errors.unexpectedEnd: "Bug Risk/Unexpected End of Input"
  }

  Severity = {
    # -- Warnings
    Warnings.messageCase: "major",
    Warnings.enumTypeCase: "major",
    Warnings.serviceCase: "major",
    Warnings.fieldCase: "minor",
    Warnings.enumValueCase: "minor",
    Warnings.rpcMethodCase: "minor",

    # -- Errors
    Errors.fileNotFound: "critical",
    Errors.importUnresolved: "critical",
    Errors.notDefined: "critical",
    Errors.missingFieldNumber: "critical",
    Errors.unexpectedToken: "critical",
    Errors.unexpectedEnd: "critical"
  }

  SeverityHandler = {
    "major": output.error,
    "minor": output.warn,
    "critical": output.critical
  }

  Remediation = {
    # -- Warnings
    Warnings.messageCase: 50000,
    Warnings.enumTypeCase: 50000,
    Warnings.serviceCase: 50000,
    Warnings.fieldCase: 50000,
    Warnings.enumValueCase: 50000,
    Warnings.rpcMethodCase: 50000,

    # -- Errors
    Errors.fileNotFound: 70000,
    Errors.importUnresolved: 70000,
    Errors.notDefined: 70000,
    Errors.missingFieldNumber: 50000,
    Errors.unexpectedToken: 50000,
    Errors.unexpectedEnd: 50000
  }

  Categories = {
    # -- Warnings
    Warnings.messageCase: ["Compatibility", "Style"],
    Warnings.enumTypeCase: ["Compatibility", "Style"],
    Warnings.serviceCase: ["Compatibility", "Style"],
    Warnings.fieldCase: ["Compatibility", "Style"],
    Warnings.enumValueCase: ["Compatibility", "Style"],
    Warnings.rpcMethodCase: ["Compatibility", "Style"],

    # -- Errors
    Errors.fileNotFound: ["Bug Risk"],
    Errors.importUnresolved: ["Bug Risk"],
    Errors.notDefined: ["Bug Risk"],
    Errors.missingFieldNumber: ["Bug Risk"],
    Errors.unexpectedToken: ["Bug Risk"],
    Errors.unexpectedEnd: ["Bug Risk"]
  }

  Message = {
    # -- Warnings
    Warnings.messageCase: "Use CamelCase (with an initial capital) for message names.",
    Warnings.enumTypeCase: "Use underscore_separated_names for field names.",
    Warnings.serviceCase: "Use CamelCase (with an initial capital) for enum type names.",
    Warnings.fieldCase: "Use CAPITALS_WITH_UNDERSCORES for enum value names.",
    Warnings.enumValueCase: "Use CamelCase (with an initial capital) for service names.",
    Warnings.rpcMethodCase: "Use CamelCase (with an initial capital) for RPC method names.",

    # -- Errors
    Errors.fileNotFound: "File not found: %(file)s.",
    Errors.importUnresolved: "Import was not found or had errors: %(context)s.",
    Errors.notDefined: "Symbol \"%(context)s\" was not defined.",
    Errors.missingFieldNumber: "Missing field number",
    Errors.unexpectedToken: "Expected token: \"%(context)s\".",
    Errors.unexpectedEnd: "Unexpected end of input, missing '}'"
  }

  ## -- Internals -- ##
  __config = None  # config for the linter, parsed from JSON
  __raw_output = None  # raw output from `protoc-gen-lint`
  __issues = None  # issues detected during the lint process
  __exit = 0  # exit code to use when done
  __arguments = None  # arguments from the CLI
  __protofiles = None  # frozenset of files found for scanning
  __regexes = None  # regex compiler cache

  # @TODO(sgammon): add __slots__

  def __init__(self, config, arguments):

    """ Initialize the main `Linter` object.

        :param config: `config.LinterConfig` object. """

    self.__config = config
    self.__issues = []
    self.__arguments = arguments
    self.__regexes = {}

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

  def __compile_regex(self, formula):

    """ Compile a regex exclude_path.

        :param formula: Regex formula.
        :returns: Compiled regex, which can be cached. """

    if formula in self.__regexes:
      return self.__regexes[formula]
    regex = re.compile(formula)
    self.__regexes[formula] = regex
    return regex

  def __exclude_match(self, path, exclude_path):

    """ See if a path candidate to be scanned could match a configured
        exclude path.

        :param path: Path to scan, potentially.
        :param exclude_path: Path configured for exclusion.
        :returns: `True` if `path` should be excluded, due to matching `exclude_path`. """

    # simple prefix match
    if not path.startswith(exclude_path):
      # regex match maybe?
      try:
        regex = self.__compile_regex(exclude_path)
        if regex:
          result = regex.match(path)
          if result:
            output.say("Path '%s' excluded by exclusion path '%s'." % (path, exclude_path))
            return True  # should be excluded
          else:
            return False  # did not match
      except ValueError:
        output.say("Unable to compile exclude_path as regex: '%s'" % exclude_path)
      return False  # did not exclude
    return True  # should be excluded

  def __command(self, base):

    """ Generate command flags to pass to `protoc`.

        :param base: Initial command arguments.
        :return: Command flags, based on config. """

    prefixes = []
    protofiles = []
    exclude_paths = self.config.exclude_paths
    include_paths = self.config.include_paths

    for configured_path in include_paths:

      # handle excluded paths
      if configured_path in exclude_paths or (
        any(filter(lambda exclude_path: self.__exclude_match(configured_path, exclude_path), exclude_paths))):
        output.say('Skipping excluded path "%s".' % configured_path)
        continue

      protofile_batch = []
      include_path = self.__make_abspath(configured_path)

      if os.path.isdir(include_path):
        prefixes.append('--proto_path=%s' % include_path)

        output.say('Scanning include_path "%s"...' % include_path)

        for protofile in self.__scan(include_path):
          if protofile:
            protofile_batch.append(protofile)

        if __debug__:
          if len(protofile_batch) == 0:
            output.say('Found no protos.')
          else:
            output.say('Found %s protos:' % str(len(protofile_batch)))
            for proto_file in protofile_batch:
              output.say('- %s' % proto_file)

        if len(protofile_batch) > 0:
          protofiles.extend(protofile_batch)

    if len(protofiles) == 0:
      output.say("No files to analyze. Exiting.")
      sys.exit(0)

    base.extend(prefixes)
    base.extend(protofiles)
    self.__protofiles = frozenset(protofiles)
    base.append('--lint_out=/.linter')
    return base

  def __resolve_warning(self, issue_msg):

    """ Resolve a unique enumerated code for this issue so
        it may be understood for severity and remediation.

        :param issue_msg: Parsed message from the issue.
        :returns: Enumerated `Warning` type for this issue.
        :raises ValueError: If the `Warning` type cannot be parsed. """

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

  def __resolve_error(self, error_msg):

    """ Resolve a unique enumerated code for a potential error so
        it may be understood for severity and remediation.

        :param error_msg: Potential error message from the compiler.
        :returns: Enumerated `Error` type for this issue, or `None`. """

    # @TODO(sgammon): fork/file PRs to get issue ID output from plugin
    # from: https://github.com/ckaznocha/protoc-gen-lint/blob/master/linter/linter.go#L32

    if 'file not found' in error_msg:
      return Linter.Errors.fileNotFound
    elif 'was not found or had errors' in error_msg:
      return Linter.Errors.importUnresolved
    elif 'is not defined' in error_msg:
      return Linter.Errors.notDefined
    elif 'missing field number' in error_msg:
      return Linter.Errors.missingFieldNumber
    elif 'expected' in error_msg:
      return Linter.Errors.unexpectedToken
    elif 'reached end of input' in error_msg:
      return Linter.Errors.unexpectedEnd
    return None

  def __resolve_context(self, resolved_error, error_message):

    """ Resolve contextual information during the parsing of an error
        emitted by the `protoc` compiler.

        :param resolved_error: `Error` type.
        :param error_message: Error message to parse.
        :returns: Context related to the error to include. """

    error_sample = error_message.lower().strip()
    if resolved_error == Linter.Errors.fileNotFound:
      return  # context is not supported for file-not-found stuff
    elif resolved_error == Linter.Errors.unexpectedEnd:
      return  # no context needed
    elif resolved_error == Linter.Errors.missingFieldNumber:
      return  # compiler provides no context for missing field number errors
    elif resolved_error == Linter.Errors.importUnresolved:
      error_split = error_message.split("\"")
      if len(error_split) > 2 and ".proto" in error_split[1]:
        # it's an import error, the context is in the second position
        return error_split[1]
    elif resolved_error in frozenset((
      Linter.Errors.unexpectedToken, Linter.Errors.notDefined)):
      error_split = error_message.split("\"")
      if len(error_split) > 2:
        # return the symbol that failed
        return error_split[1]
    raise NotImplementedError("Error is unimplemented for context: '%s'" % error_message)

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

      if not len(issue_split) == 2:
        # it could be an error from the compiler
        compiler_split = raw_issue.split(': ')
        if len(compiler_split) == 2:
          # still could be an error
          error_file, error_message = tuple(map(lambda x: x.strip(), compiler_split))
          resolved_error = self.__resolve_error(error_message.lower())
          if resolved_error:
            context = self.__resolve_context(resolved_error, error_message)

            error_positional = (
              raw_issue,
              resolved_error,
              error_message)

            error_context = {
              'protocontext': context}

            if ":" in error_file:
              # it may have a line and column
              error_file_split = error_file.split(':')
              if len(error_file_split) > 1:
                if len(error_file_split) == 2:
                  # it's a line number
                  error_file, error_line = tuple(map(lambda x: x.strip(), error_file_split))
                  error_context.update({
                    "protofile": error_file,
                    "protoline": int(error_line)})
                elif len(error_file_split) == 3:
                  # it's a line number and a column number
                  error_file, error_line, error_column = tuple(map(lambda x: x.strip(), error_file_split))
                  error_context.update({
                    "protofile": error_file,
                    "protoline": int(error_line),
                    "protocolumn": int(error_column)})

            yield Error(self, *error_positional, **error_context)
            continue

        # not an error
        raise NotImplementedError("No way to handle output: '%s'" % raw_issue)

      else:
        # it's output from the linter
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
          self,
          raw=raw_issue,
          type=self.__resolve_warning(issue_message),
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

  def make_path_for_protofile(self, protofile):

    """ Make an absolute link for a protofile.

        :param protofile: Protobuf file postfix.
        :return: Path to protofile from workspace root. """

    resolved_path = None
    for path in self.protofiles:
      if path.endswith(protofile):
        resolved_path = path

    if not resolved_path:
      raise ValueError("unable to resolve absolute path for protobuf file: %s" % protofile)

    resolved_path = resolved_path.replace(self.workspace, "")
    if resolved_path.startswith("/"):
      return "/".join(resolved_path.split("/")[1:])
    return resolved_path

  ## -- Properties -- ##
  @property
  def config(self):

    """ Return the active config for this linter.
        :returns: `config.LinterConfig` for this linter. """

    return self.__config

  @property
  def protofiles(self):

    """ Return the files being scanned by the linter.
        :returns: Files being scanned. """

    return self.__protofiles

  @property
  def workspace(self):

    """ Returns the workspace being scanned.
        :returns: Current workspace. """

    return self.__config.workspace

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


class BaseIssue(object):

  """ Base issue object, shared by `Issue` and `Error` for common functionality. """

  ## -- Internals -- ##
  __raw = None  # raw output for this issue
  __type = None  # parsed type of this issue
  __linter = None  # linter that created this
  __message = None  # message that was emitted
  __protofile = None  # protobuf file that caused the issue
  __protoline = None  # protobuf line in file that caused the issue
  __protocolumn = None  # protobuf column in line that caused the issue
  __protocontext = None  # protobuf extra context related to issue

  def __init__(self,
               linter,
               raw,
               type,
               message,
               protofile=None,
               protoline=None,
               protocolumn=None,
               protocontext=None):

    """ Initialize a detected issue from the `protoc-gen-lint` tool.

        :param linter: The linter that created this object.
        :param raw: Raw line as emitted by the tool.
        :param type: Parsed type of `Warning` from `raw`.
        :param code: Numeric code corresponding to this issue type.
        :param message: Message emitted by the tool, parsed from `raw`.
        :param protofile: Protobuf file that caused the issue.
        :param protoline: Line in the protobuf file that caused the issue. """

    self.__linter = linter
    self.__type = type
    self.__raw = raw
    self.__protofile = protofile
    self.__protoline = protoline
    self.__protocolumn = protocolumn
    self.__protocontext = protocontext
    self.__message = Linter.Message[type] % self.render_context()

  ## -- Properties -- ##
  @property
  def raw(self):

    """ Return the raw, unparsed line emitted by `protoc-gen-lint` for this issue.
        :returns: Raw output line. """

    return self.__raw

  @property
  def type(self):

    """ Return the type of this issue.
        :returns: `linter.Linter.Warnings` type for this issue. """

    return self.__type

  @property
  def linter(self):

    """ Return the linter that created this issue.
        :returns: `linter.Linter`. """

    return self.__linter

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

  ## -- Methods -- ##
  def render_context(self):

    """ Return a context for rendering snippets of text.
        :returns: Dictionary context for rendering messages. """

    return {
      "file": self.file,
      "line": self.line,
      "column": self.column,
      "context": self.context,
      "type": self.type,
      "message": self.message,
      "raw": self.raw
    }

  def serialize(self, exported):

    """ Serialize the exported version of this structure for use with CodeClimate.
        :returns: JSON-serialized exported object. """

    return json.dumps(exported) + "\0"

  def write(self):

    """ Write this issue to `stdout` in a JSON-serialized structure
        that CodeClimate is capable of reading. """

    output.say('Writing issue "%s"...' % repr(self))
    Linter.SeverityHandler[Linter.Severity[self.type]]("[%s]: %s" % (self.__type.name, self.__message))
    output.issue(self)

  def format_location(self):

    """ Format a location for display.
        :returns: Formatted location. """

    if self.line and not self.column:
      return "%(file)s:%(line)s" % self.render_context()
    elif self.line and self.column:
      return "%(file)s:%(line)s:%(column)s" % self.render_context()
    return self.file

  def format_context(self):

    """ Format a context for display.
        :returns: Formatted context. """

    if not self.context:
      return " "
    return " context='%s', " % self.context

  def __call__(self):

    """ Dispatch `self.serialize` on the exported form of this object, which prepares
        it to be pulled into CodeClimate.

        :returns: Exported and serialized version of this issue. """

    return self.serialize(self.export())


class Issue(BaseIssue):

  """ Represents a detected issue by `protoc-gen-lint` that has been parsed
      from the plugin output and now provided here. """

  def __repr__(self):

    """ Generate a string representation of this object. """

    return "Issue(location=%s,%smessage='%s')" % (
      self.format_location(),
      self.format_context(),
      self.message)

  ## -- Properties -- ##
  @property
  def unique_hash(self):

    """ Calculate and return a unique hash for this issue.
        :returns: Unique hash, as a hex digest, for this specific issue. """

    return hashlib.sha256('::'.join((map(unicode, (
      "v1",
      self.type.name,
      self.message,
      self.file,
      self.line,
      self.column,
      self.context))))).hexdigest()

  def export(self):

    """ Export this object to a dictionary that describes it so it may be written
        to `stdout` to be handled by CodeClimate.

        :returns: Exported `dict` to pass to CodeClimate. """

    return {
      "type": "issue",
      "check_name": Linter.Names[self.type],
      "description": Linter.Message[self.type] % self.render_context(),
      "categories": Linter.Categories[self.type],
      "severity": Linter.Severity[self.type],
      "fingerprint": self.unique_hash,
      "location": {
        "path": self.linter.make_path_for_protofile(self.file),
        "positions": {
          "begin": {
            "line": self.line,
            "column": self.column
          },
          "end": {
            "line": self.line,
            "column": self.column
          }
        }
      }
    }


class Error(BaseIssue):

  """ Represents an error emitty by `protoc` that has been parsed from the
      compiler output and now provided here. """

  ## -- Internals -- ##
  def __repr__(self):

    """ Generate a string representation of this object. """

    return "Error(location=%s,%smessage='%s')" % (
      self.format_location(),
      self.format_context(),
      self.message)

  ## -- Properties -- ##
  @property
  def unique_hash(self):

    """ Calculate and return a unique hash for this error.
        :returns: Unique hash, as a hex digest, for this specific error. """

    return hashlib.sha256('::'.join((map(unicode, (
      "v1",
      self.type.name,
      self.message,
      self.file))))).hexdigest()

  def export(self):

    """ Export this object to a dictionary that describes it so it may be written
        to `stdout` to be handled by CodeClimate.

        :returns: Exported `dict` to pass to CodeClimate. """

    return {
      "type": "issue",
      "check_name": Linter.Names[self.type],
      "description": Linter.Message[self.type] % self.render_context(),
      "categories": Linter.Categories[self.type],
      "severity": Linter.Severity[self.type],
      "fingerprint": self.unique_hash,
      "location": {
        "path": self.linter.make_path_for_protofile(self.file),
        "positions": {
          "begin": {
            "line": 0,  # @TODO(sgammon): is this the best way to express a whole file?
            "column": 0
          },
          "end": {
            "line": 0,
            "column": 0
          }
        }
      }
    }
