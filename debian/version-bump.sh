#!/bin/sh

version=`dpkg-parsechangelog | grep Version | sed -ne "1{s/^Version: \(.*\)/\1/;p}"`
echo "version = '$version'"  > debian/hh-tornado-protobuf-utils/usr/share/pyshared/protoctor/__init__.py