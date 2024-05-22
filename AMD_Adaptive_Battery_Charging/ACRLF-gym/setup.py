# setup.py
# downloads dependency packages for the required environment
# add required packages in install_requires
# 
# Copyright (c) 2023 Advanced Micro Devices Inc.
# Report Bugs to Shamith Achanta <Shamith.Achanta@amd.com>
#

from setuptools import setup

setup(name="ACRLF",
    version='0.0.1',
    author="Shamith Achanta",
    author_email="Shamith.Achanta@amd.com",
    install_requires=["gym==0.17.2", "numpy>=1.18.0", "psutil", "pandas", "scikit-learn", "jdatetime", "wmi"]
)