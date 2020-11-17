from os import path
from codecs import open

from setuptools import setup, find_packages

# Get the directory where this current file is saved
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='changelog-neuropoly',
    version='1.0.1',
    python_requires='>=3.5',
    description='Create a changelog file from all the merged pull requests.',
    url='https://github.com/neuropoly/changelog',
    author='NeuroPoly Lab, Polytechnique Montreal',
    author_email='neuropoly@googlegroups.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='',
    install_requires=['requests'],
    packages=find_packages(exclude=['.git']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'changelog=changelog.changelog:main',
        ],
    },
)
