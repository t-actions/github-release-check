#!/bin/sh

set -ex

for d in */ ; do
    cd $d
    if ls *.sha256 1>/dev/null 2>&1; then
        sha256sum -c *.sha256
    fi
    cd ..
done
