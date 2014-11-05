# coding=utf-8

import os

from hhwebutils.packaging import parse_version_from_changelog


version = parse_version_from_changelog(
    'hh-tornado-protobuf-utils', os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
