
#
## `protolint`: Makefile
#

# required tools: python, virtualenv

# - Config
VERBOSE ?= no
ENV ?= .env
BIN ?= $(ENV)/bin/
BUILD_TARGETS ?= build build_py build_scripts
RELEASE_TARGETS ?= sdist bdist bdist_dumb

DOCKER_TAG ?= latest
DOCKER_BUILD_ARGS ?= --rm --pull --tag

TARGET ?= build
DIST ?= dist

# - Tools
PROTOC ?= $(shell which protoc)
PROTOC_GEN_LINT ?= $(shell which protoc-gen-lint)

ifeq ($(VERBOSE),yes)
RM_FLAGS = -frv
CP_FLAGS = -frv
else
RM_FLAGS = -fr
CP_FLAGS = -fr
endif

define say
	@echo $1
endef


all: clean $(TARGET) link test release image
	$(call say,"'protolint' is ready.")

clean:
	$(call say,"Cleaning 'protolint' build targets...")
	@rm $(RM_FLAGS) $(TARGET) $(DIST)

	$(call say,"Cleaning ephemeral files...")
	@find . -name .DS_Store -delete
	@find . -name *.pyc -delete
	@find . -name *.pyo -delete

distclean: clean
	$(call say,"Resetting 'protolint'...")
	@rm $(RM_FLAGS) $(ENV)

forceclean: distclean
	$(call say,"Sanitizing 'protolint'...")
	@git reset --hard
	@git clean -xdf

$(TARGET): environment dependencies
	$(call say,"Building 'protolint'...")
	@python setup.py $(BUILD_TARGETS)

test:
	$(call say,"Running 'protolint' testsuite...")
	@mkdir -p $(ENV)/coverage $(ENV)/tests
	@$(BIN)/nosetests --with-coverage --cover-package=protolint --with-xunit --xunit-file=$(ENV)/tests/tests.xml --cover-xml --cover-xml-file=$(ENV)/coverage/coverage.xml

release: $(DIST)
$(DIST):
	$(call say,"Cutting 'protolint' release...")
	@python setup.py $(RELEASE_TARGETS)

image:
	$(call say,"Building 'protolint' image...")
	@docker build $(DOCKER_BUILD_ARGS) protolint:$(DOCKER_TAG) .

link:
	$(call say,"Resolving tools...")
	@-ln -s $(PROTOC) .env/bin/protoc
	@-ln -s $(PROTOC_GEN_LINT) .env/bin/protoc-gen-lint


## -- Tasks

dependencies:
	$(call say,"Installing dependencies for 'protolint'...")
	@$(BIN)easy_install pip
	@$(BIN)pip install -r requirements.txt

environment: $(ENV)

$(ENV):
	$(call say,"Setting up virtualenv...")
	@mkdir $(ENV)
	@virtualenv --prompt="[protolint]: " $(ENV)


.PHONY: all clean distclean forceclean test link
