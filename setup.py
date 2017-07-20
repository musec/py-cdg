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
    'name': 'cgnet',
    'description': 'Software callgraph manipulation',
    'author': 'Jonathan Anderson',
    'author_email': 'jonathan.anderson@mun.ca',
    'url': 'https://github.com/musec/py-cgnet',
    'download_url': 'https://github.com/musec/py-cgnet',
    'version': '0.1',
    'install_requires': ['networkx', 'nose', 'pygraphviz'],
    'packages': ['cgnet'],
    'scripts': ['bin/cgdot'],
    'test_suite': 'nose.collector',
    'tests_require': ['nose'],
}

setup(**config)
