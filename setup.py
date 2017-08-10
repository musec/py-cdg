#!/usr/bin/env python
#
# Copyright 2017 Jonathan Anderson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'cdg',
    'description': 'Library for working with call- and data-flow graphs',
    'author': 'Jonathan Anderson',
    'author_email': 'jonathan.anderson@mun.ca',
    'url': 'https://github.com/musec/py-cdg',
    'download_url': 'https://github.com/musec/py-cdg',
    'install_requires': ['networkx', 'pygraphviz'],
    'packages': ['cdg'],
    'scripts': ['bin/cdg'],
    'setup_requires': ['setuptools_scm'],
    'test_suite': 'nose.collector',
    'tests_require': ['nose'],
    'use_scm_version': True,
}

setup(**config)
