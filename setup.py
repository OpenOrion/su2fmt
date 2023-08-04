

from setuptools import setup

setup(
   name='su2fmt',
   version='2.0.0',
   description='the open source SU2 mesh format parser and exporter',
   author='Afshawn Lotfi',
   author_email='',
   packages=['su2fmt'],
   install_requires=[
    "numpy",
   ]
)