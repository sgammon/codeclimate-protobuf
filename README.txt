
# protolint
## support for `protobuf` in CodeClimate

This tool wraps protoc-gen-lint to generate improvement suggestions for your .protos. It then outputs those items in CodeClimate's JSON format, so it can be used as a CodeClimate Engine.


### How it works

It's a Python module called 'protolint', with a module-level run file ('__main__.py'). It can be executed via any of the following methods:

Via the local bash script:
./protolint.sh <args...>

Via the virtualenv:
./activate && protolint <args...>

After installing globally, you can additionally execute it via:

Global module in Python:
python -m protolint <args...>

CLI tool:
protolint <args...>

The tool should output messages to `stderr` and JSON-formatted issues to `stdout`.
