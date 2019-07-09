#!/bin/bash

set -ex

WORK_DIR=$(dirname $(readlink -f $0))
HUE_SRC=$(realpath $WORK_DIR/../..)
BUILD_DIR=$(realpath $HUE_SRC/../containerbuild$GBN)
HUE_DIR=$WORK_DIR/hue
APACHE_DIR=$WORK_DIR/huelb

compile_hue() {
  mkdir -p $BUILD_DIR
  cd $HUE_SRC
  PREFIX=$BUILD_DIR make install
  $BUILD_DIR/hue/tools/virtual-bootstrap/virtual-bootstrap.py --relocatable "$BUILD_DIR/hue/build/env"
}

docker_hue_build() {
  cd $HUE_DIR
  cp -a $BUILD_DIR/hue $HUE_DIR
  docker build -f $HUE_DIR/Dockerfile -t hue:$GBN .
}

docker_huelb_build() {
  cd $APACHE_DIR
  cp -a $BUILD_DIR/hue/build/static $APACHE_DIR
  docker build -f $APACHE_DIR/Dockerfile -t huelb:$GBN .
}

compile_hue
docker_hue_build
docker_huelb_build
