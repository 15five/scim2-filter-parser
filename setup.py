#!/usr/bin/env python

from setuptools import setup, find_packages
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def long_description():
    """Get the long description from the README"""
    return open(os.path.join(BASE_DIR, 'README.rst')).read()


setup(
    name='scim2-filter-parser',
    version='0.3.4',
    description='A customizable parser/transpiler for SCIM2.0 filters',
    url='https://github.com/15five/scim2-filter-parser',
    maintainer='Paul Logston',
    maintainer_email='paul@15five.com',
    author='Paul Logston',
    author_email='paul@15five.com',
    keywords='scim 2.0 filter',
    license='MIT',
    long_description=long_description(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'sly==0.3',
    ],
    entry_points={
        'console_scripts': [
            'sfp-lexer=scim2_filter_parser.lexer:main',
            'sfp-parser=scim2_filter_parser.parser:main',
            'sfp-transpiler=scim2_filter_parser.transpiler:main',
            'sfp-query=scim2_filter_parser.query:main',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
