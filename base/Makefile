
#
## `protolint`: Base Image Makefile
#

# required tools: docker


all: image
	$(call say,"Base image is ready.")

image:
	$(call say,"Building 'protoc-alpine' image...")
	@docker build $(DOCKER_BUILD_ARGS) sgammon/protoc-alpine:$(DOCKER_TAG) .

push:
	$(call say,"Pushing 'protoc-alpine' image...")
	@docker push sgammon/protoc-alpine:$(DOCKER_TAG)


.PHONY: all image push

