#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# requirements
install_requires = [
    "six>=1.10.0",
    "mysql-replication==0.8",
]

setup(name="mysql-eventprocessor",
      version=__import__("mysqlevp").__version__,
      description="daemon interface for handling MySQL binary log events",
      author="zako",
      author_email="jffifa@gmail.com",
      packages=find_packages(),
      url="https://github.com/jffifa/python-mysql-eventprocessor",
      license="MIT",
      install_requires=install_requires,
      classifiers=[
          "Topic :: Database",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: Implementation :: CPython",
      ])
