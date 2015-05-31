import os
from setuptools import setup

setup(
    name = "web_plugins",
    version = "0.0.1",
    author = "Matt Riley",
    author_email = "mattriley@oscmp.com",
    description = "Utilities to build python webapps",
    license = "BSD",
    keywords = "Utilities to build python webapps",
    url = "http://www.oscmp.com/web_plugins",
    packages=['web_plugins'],
    long_description='README',
    setup_requires=['uwsgi', 'pystache'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    package_data = {'':'*.md'},
)
