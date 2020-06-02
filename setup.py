#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'httpx==0.12.0',
]
test_requirements = [
    'mock',
    'pytest-mock',
    'pytest-asyncio',
    'pytest>=3',
]

with open('README.md', 'r', encoding='utf-8') as fh:
    readme = fh.read()

setup(
    name='coresender',
    version='1.0.1',
    description='Coresender API for sending email',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Marcin Sztolcman',
    author_email='opensource@coresender.com',
    url='https://coresender.com',
    packages=find_packages(),
    package_data={'': ['LICENSE', ]},
    package_dir={'coresender': 'coresender'},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Environment :: Web Environment',
    ],
    tests_require=test_requirements,
    extras_require={
    },
    project_urls={
        'API Documentation': 'https://coresender.com/docs/api',
        'Source': 'https://github.com/coresender/coresender-sdk-py',
    },
    keywords="coresender api email smtp mta transactional",
)
