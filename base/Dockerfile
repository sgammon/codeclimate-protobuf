FROM golang:1.6.2-alpine
MAINTAINER Sam Gammon <sam@bloombox.io>

RUN apk add --update \
      autoconf \
      automake \
      build-base\
      curl \
      git \
      go \
      libtool \
      protobuf \
      python \
      bash \
      make \
      qt5-qtbase-dev

RUN go get github.com/ckaznocha/protoc-gen-lint

ENV PROTOBUF_REVISION v3.3.1
RUN git clone https://github.com/google/protobuf -b $PROTOBUF_REVISION --depth 1 \
  && cd protobuf \
  && ./autogen.sh \
  && ./configure --prefix=/usr \
  && make \
  && make check \
  && make install \
  && cd .. && rm -rf protobuf && cd

ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8
RUN ALPINE_GLIBC_BASE_URL="https://github.com/andyshinn/alpine-pkg-glibc/releases/download" \
    && ALPINE_GLIBC_PACKAGE_VERSION="2.23-r1" \
    && ALPINE_GLIBC_BASE_PACKAGE_FILENAME="glibc-$ALPINE_GLIBC_PACKAGE_VERSION.apk" \
    && ALPINE_GLIBC_BIN_PACKAGE_FILENAME="glibc-bin-$ALPINE_GLIBC_PACKAGE_VERSION.apk" \
    && ALPINE_GLIBC_I18N_PACKAGE_FILENAME="glibc-i18n-$ALPINE_GLIBC_PACKAGE_VERSION.apk" \
    && apk --update add bash \
    && apk add --no-cache --virtual=build-dependencies ca-certificates \
    && apk add bash \
    && apk add tzdata \
    && cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \
    && echo America/Sao_Paulo > /etc/timezone \
    && curl -sL \
        -O "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
        -O "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
        -O "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_I18N_PACKAGE_FILENAME" \
    && apk add --no-cache --allow-untrusted \
        "$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_I18N_PACKAGE_FILENAME" \
    && /usr/glibc-compat/bin/localedef --force --inputfile POSIX --charmap UTF-8 C.UTF-8 || true \
    && echo "export LANG=C.UTF-8" > /etc/profile.d/locale.sh \
    && apk del glibc-i18n \
    && apk del build-dependencies \
    && rm \
        "$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_I18N_PACKAGE_FILENAME"

# Needed shared libraries and tools by protobuf and their plugins
RUN apk --update add \
  bash \
  libstdc++ \
  qt5-qtbase

# Cleaning up
RUN apk del \
  autoconf \
  automake \
  build-base \
  curl \
  git \
  libtool \
  qt5-qtbase-dev \
  && rm -rf /var/cache/apk/*
