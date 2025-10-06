"""
Setup script for MIM HyperControl.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mim-hypercontrol",
    version="1.0.0",
    author="Philip David Suh, Siyuan Qiu",
    author_email="psuh@stanford.edu, sq2234@stanford.edu", 
    description="A comprehensive GUI application for controlling MIM experiments",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/philipsuh004/mim_hypercontrol",  
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mim-hypercontrol=src.gui.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["assets/images/*.jpg", "assets/icons/*"],
    },
)
