"""
Setup script for the NeuralLog SDK.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neurallog-sdk",
    version="1.0.0",
    author="NeuralLog Team",
    author_email="info@neurallog.com",
    description="Python SDK for NeuralLog - A logging system for AI applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NeuralLog/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
)
