try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'cgnet',
    'description': 'Software callgraph manipulation',
    'author': 'Jonathan Anderson',
    'url': 'https://github.com/musec/py-cgnet',
    'download_url': 'https://github.com/musec/py-cgnet',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': [ 'flask', 'networkx', 'pygraphviz' ],
    'scripts': [],
}

setup(**config)
