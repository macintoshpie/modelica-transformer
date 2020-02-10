#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
  install_requirements = f.readlines()

setup(
  name = "modelicaTransformer",
  version = "0.1.0",
  author = "Ted Summer",
  author_email = "ted@devetry.com",
  description = ("Allows parsing and modifying Modelica files"),
  install_requires=install_requirements,
  packages=find_packages()
)