#!/usr/bin/env python
import codecs
import os
import re
import setuptools
import glob

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


test_requirements = [
        "parameterized>=0.7.0",
        "flake8>=3.7.7"
]


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
    package_data={'matrix_registration': ['*.txt','*.json',
                                          'translations/*.yaml',
                                          'templates/*.html',
                                          'static/css/*.css',
                                          'static/fonts/*.woff2',
                                          'static/images/*.jpg',
                                          'static/images/*.png',
                                          'static/images/*.ico']},
    python_requires='~=3.7',
    install_requires=[
        "alembic>=1.3.2",
        "appdirs>=1.4.3",
        "Flask>=1.1",
        "Flask-SQLAlchemy>=2.5.1",
        "flask-cors>=3.0.7",
        "flask-httpauth>=3.3.0",
        "flask-limiter>=1.1.0",
        "PyYAML>=5.1",
        "jsonschema>=3.2.0",
        "requests>=2.22",
        "SQLAlchemy>=1.3.13",
        "waitress>=2.0.0",
        "WTForms>=2.1"
    ],
    tests_require=test_requirements,
    extras_require={
        "postgres":  ["psycopg2-binary>=2.8.4"],
        "testing": test_requirements
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    entry_points={
        'console_scripts': [
            'matrix-registration=matrix_registration.app:cli'
        ],
    },
    data_files=[
        ("config", ["config.sample.yaml"]),
        (".", ["alembic.ini"]),
        ("alembic", ["alembic/env.py"]),
        ("alembic/versions", glob.glob("alembic/versions/*.py"))
    ]
)
