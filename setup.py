#!/usr/bin/env python
import codecs
import os
import re
import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name='matrix-registration',
    version=find_version("matrix_registration", "__init__.py"),
    description='token based matrix registration app',
    author='Jona Abdinghoff (ZerataX)',
    author_email='mail@zera.tax',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zeratax/matrix-registration",
    packages=['matrix_registration'],
    package_data={'matrix_registration': ['*.txt',
                                          'templates/*.html',
                                          'static/css/*.css',
                                          'static/images/*.jpg',
                                          'static/images/*.png',
                                          'static/images/*.ico']},
    include_package_data=True,
    python_requires='~=3.6',

    install_requires=[
        "appdirs==1.4.3",
        "Flask>=1.0.2",
        "flask-cors==3.0.7",
        "flask-httpauth==3.2.4",
        "flask-limiter==1.0.1",
        "python-dateutil>=2.7.3",
        "PyYAML>=5.1",
        "requests>=2.21.0",
        "WTForms>=2.2.1"
    ],
    tests_require=[
        "parameterized==0.7.0",
        "flake8==3.7.7"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    entry_points="""
        [console_scripts]
        matrix_registration=matrix_registration.__main__:main
    """,
    test_suite="tests.test_registration",
    data_files=[
        ("config", ["config.sample.yaml"]),
    ]
)
