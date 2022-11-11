from setuptools import setup
from setuptools import find_packages
import os
import re

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# with open('megnet/__init__.py', encoding='utf-8') as fd:
#     try:
#         lines = ''
#         for item in fd.readlines():
#             item = item
#             lines += item + '\n'
#     except Exception as exc:
#         raise Exception('Caught exception {}'.format(exc))


# version = re.search('__version__ = "(.*)"', lines).group(1)


setup(
    name="gcodepylot",
    version="0.1",
    description="Control gcode-based XYZ motion devices.",
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
    # extras_require={
    #     'model_saving': ['h5py'],
    #     'molecules': ['openbabel', 'rdkit'],
    #     'tensorflow': ['tensorflow>=2.1'],
    #     'tensorflow with gpu': ['tensorflow-gpu>=2.1'],
    # },
    packages=find_packages(),
    # package_data={
    #     "": [
    #     ],
    # },
    include_package_data=True,
    keywords=["robotics", "gcode", "automation"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # entry_points={
    #     'console_scripts': [
    #         'meg = megnet.cli.meg:main',
    #     ]
    # }
)
