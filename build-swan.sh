#!/bin/bash
set -x

export BUILD_DIR=/build-dir/$OS_VER
export INSTALL_DIR=/install-dir/$OS_VER
source env.sh

mkdir -p $BUILD_DIR
mkdir -p $INSTALL_DIR

# Foundation
source mpich.sh
source swan.sh
