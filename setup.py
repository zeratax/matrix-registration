#!/usr/bin/env python
import setuptools
import sys
import glob
import matrix_registration


setuptools.setup(
    name='matrix-registration',
    version=matrix_registration.__version__,
    description='token based matrix registration app',
    author='Jona Abdinghoff (ZerataX)',
    author_email='mail@zera.tax',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zeratax/matrix-registration",
    packages=setuptools.find_packages(),
    python_requires='~=3.6',

    install_requires=[
        "Flask>=1.0.2",
        "python-dateutil>=2.7.3",
        "PyYAML>=5.1",
        "requests>=2.21.0",
        "WTForms>=2.2.1"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points="""
        [console_scripts]
        matrix_registration=matrix_registration.__main__:main
    """,
    data_files=[
        ("config", ["config.sample.yaml"]),
    ],
)
