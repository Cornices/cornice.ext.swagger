""" Setup file.
"""
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()
CHANGES = open(os.path.join(here, "CHANGES.rst")).read()

REQUIREMENTS = [
    'six',
    'cornice',
    'colander',
]

REQUIREMENTS_DEV = [
    'coverage',
    'coveralls',
    'flake8',
    'flex',
    'mock',
    'pyramid',
    'pytest',
    'pytest-cache',
    'pytest-capturelog',
    'pytest-cover',
    'pytest-sugar',
    'tox',
    'webtest'
]

setup(
    name="cornice_swagger",
    version='0.7.0',
    description="Generate swagger from a Cornice application",
    long_description=README + "\n\n" + CHANGES,
    license="Apache License (2.0)",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="web services",
    author="Josip Delic",
    author_email="delijati@gmx.net",
    url="https://github.com/Cornices/cornice.ext.swagger",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_DEV,
    test_suite='tests',
)
