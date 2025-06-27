"""
Setup script for AI Workbench

This script allows the AI Workbench to be installed as a Python package.
"""

import os
import sys
from setuptools import setup, find_packages

# Read the README.md for the long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Define package metadata
NAME = 'ai-workbench'
VERSION = '1.0.0'
DESCRIPTION = 'Advanced system monitoring and optimization tool with AI capabilities'
AUTHOR = 'OPRYXX Team'
AUTHOR_EMAIL = 'opryxx@example.com'
URL = 'https://github.com/yourusername/ai-workbench'
LICENSE = 'MIT'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Operating System :: OS Independent',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
]

# Define dependencies
INSTALL_REQUIRES = [
    'psutil>=5.9.0',
    'sqlalchemy>=1.4.0',
    'alembic>=1.7.0',
    'pydantic>=1.9.0',
    'python-dotenv>=0.19.0',
    'pywin32>=303; sys_platform == "win32"',
    'wmi>=1.5.1; sys_platform == "win32"',
    'py-cpuinfo>=8.0.0',
    'py-cpuinfo>=8.0.0',
    'py-cpuinfo>=8.0.0',
]

# Development dependencies
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=6.0.0',
        'pytest-cov>=2.0.0',
        'black>=21.0',
        'isort>=5.0.0',
        'mypy>=0.900',
        'pylint>=2.12.0',
        'sphinx>=4.0.0',
        'sphinx-rtd-theme>=0.5.0',
    ],
    'gui': [
        'PyQt5>=5.15.0',
        'pyqtgraph>=0.12.0',
        'qtawesome>=1.0.0',
    ],
    'ml': [
        'numpy>=1.20.0',
        'pandas>=1.3.0',
        'scikit-learn>=1.0.0',
        'tensorflow>=2.6.0; sys_platform != "win32" or (sys_platform == "win32" and python_version >= "3.9")',
        'torch>=1.9.0',
    ],
}

# Entry points
ENTRY_POINTS = {
    'console_scripts': [
        'ai-workbench=ai_workbench.__main__:main',
    ],
}

# Package data
PACKAGE_DATA = {
    'ai_workbench': [
        'config/*.json',
        'models/*.pkl',
        'templates/*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/img/*',
    ]
}

# Setup configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    packages=find_packages(include=['ai_workbench', 'ai_workbench.*']),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    package_data=PACKAGE_DATA,
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
)
