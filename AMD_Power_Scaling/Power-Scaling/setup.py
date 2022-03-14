# setup.py
# downloads dependency packages for the required environment
# add required packages in install_requires
# 
# Copyright (c) 2022 Shamith Achanta
# Report Bugs to Shamith Achanta <shamith2@illinois.edu>
#

from setuptools import setup

setup(name="Power_Scaling",
    version='0.0.1',
    author="Shamith Achanta",
    author_email="shamith2@illinois.edu",
    install_requires=["gym==0.21.0", "numpy>=1.18.0"]
)