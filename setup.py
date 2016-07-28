#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#
#  Created by TVA on 4/19/16.
#  Copyright (c) 2016 django-query-execfile. All rights reserved.
#

from setuptools import setup, find_packages

__version__ = '0.2'

setup(
	name='drf-routers',
	version=__version__,
	description='Grouped/Nested resources for the Django Rest Framework',
	author='V.Anh Tran',
	author_email='tranvietanh1991@gmail.com',
	license="MIT",
	url='https://github.com/tranvietanh1991/drf-routers',  # use the URL to the github repo
	download_url='https://github.com/tranvietanh1991/drf-routers/archive/master.zip',  # source code download
	packages=find_packages(exclude=['*.tests', '*.tests.*']),
	include_package_data=True,
	install_requires=[
		"Django>=1.7",
	],
	keywords=['django', 'rest', 'drf', 'django-rest-framwork', 'router', 'nested', 'grouped'],  # arbitrary keywords
	classifiers=[
		"Development Status :: 4 - Beta",
		"Environment :: Web Environment",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"Intended Audience :: System Administrators",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 2",
		# "Programming Language :: Python :: 3",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
)