
#
## `protolint`: Base Image Makefile
#

# required tools: docker

PWD ?= $(shell pwd)


all: image
	$(call say,"Base image is ready.")

protoc-gen-lint:
	$(call say,"Building containerized proto-gen-lint...")
	@docker run -v $(PWD):/go/bin --rm golang go get github.com/ckaznocha/protoc-gen-lint

image: protoc-gen-lint
	$(call say,"Building 'protoc-alpine' image...")
	@docker build $(DOCKER_BUILD_ARGS) sgammon/protoc-alpine:$(DOCKER_TAG) .

push:
	$(call say,"Pushing 'protoc-alpine' image...")
	@docker push sgammon/protoc-alpine:$(DOCKER_TAG)


.PHONY: all image push
