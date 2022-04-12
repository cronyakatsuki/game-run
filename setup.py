#!/usr/bin/env python
from setuptools import setup
import game_run

setup(
    name='game-run',
    version=game_run.VERSION,
    description='Simple game runnner from command line.',
    url='https://github.com/cronyakatsuki/game-run',
    author='Crony Akatsuki',
    author_email='cronyakatsuki@gmail.com',
    license='GPL-3.0',
    py_modules=['game_run'],
    entry_points={
        'console_scripts': [
            'game-run=game_run:main',
        ],
    },
    keywords=['games', 'game', 'cmd', 'commandline'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: GPL-3.0 License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux'
    ],
)
