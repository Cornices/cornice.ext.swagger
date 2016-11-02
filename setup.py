""" Setup file.
"""
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()
CHANGES = open(os.path.join(here, "CHANGES.rst")).read()

requires = [
    "cornice",
    "colander",
]

setup(
    name="cornice_swagger",
    version="0.1",
    description="Generate swagger from a Cornice application",
    long_description=README + "\n\n" + CHANGES,
    license="Apache License (2.0)",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="web services",
    author="Josip Delic",
    author_email="delicj@delijati.net",
    url="https://github.com/Cornices/cornice.ext.swagger",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires, )
