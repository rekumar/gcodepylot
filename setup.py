from setuptools import setup
from setuptools import find_packages
import os
import re

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="gcodepylot",
    version="0.1",
    description="Control XYZ motion devices using GCode (Marlin firmware).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rishi Kumar",
    author_email="re.kumar@icloud.com",
    download_url="https://github.com/rekumar/gcodepylot",
    license="MIT",
    install_requires=[
        "numpy",
        "pyserial",
        "PyQt5",
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords=["robotics", "gcode", "automation", "xyz", "3d printing", "Ender 3"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
