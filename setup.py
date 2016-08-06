#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
setup(
        name = 'curlgmOo',
        version = '0.0.8',
        package = find_packages('src'),
        package_dir = {'':'src'},
        zip_safe = False,
        
        description='gearman-client as CLT',
        long_description = 'Curlgm makes it possible to request gearman service by URLs. Simple and JSON supported',
        author = 'doudou',
        author_email = 'unknow@host.com',

        licenese = 'GPL',
        keywords = ('gearman','URL','JSON'),
        plantforms='Independant',
        url ='',

        scripts=['src/bin/curlgm',]
        )
