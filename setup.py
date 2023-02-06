

from setuptools import setup

setup(
   name='su2fmt',
   version='1.0',
   description='the open source SU2 mesh format parser and visualizer',
   author='Afshawn Lotfi',
   author_email='',
   packages=['su2fmt'],
   install_requires=[
    "numpy",
    "pythreejs",
    "ipywidgets==7.6"
   ]
)