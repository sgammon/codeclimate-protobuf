
#
## `protolint`: CI Image Makefile
#

# required tools: docker


all: image
	$(call say,"CI image is ready.")

image:
	$(call say,"Building 'protolint-ci' image...")
	@docker build $(DOCKER_BUILD_ARGS) sgammon/protolint-ci:$(DOCKER_TAG) .

push:
	$(call say,"Pushing 'protolint-ci' image...")
	@docker push sgammon/protolint-ci:$(DOCKER_TAG)


.PHONY: all image push

