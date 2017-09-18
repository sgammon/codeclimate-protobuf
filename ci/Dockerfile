FROM circleci/golang:latest
MAINTAINER Sam Gammon <sam@bloombox.io>
RUN sudo apt-get update && sudo apt-get install -y protobuf-compiler python2.7 python-pip
RUN sudo pip install virtualenv
RUN go get github.com/ckaznocha/protoc-gen-lint
