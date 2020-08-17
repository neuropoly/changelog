from setuptools import setup, find_packages
from codecs import open
from os import path

# Get the directory where this current file is saved
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='changelog',
    version='1.0',
    python_requires='>=3.7',
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
    packages=find_packages(exclude=['.git']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'changelog = changelog:main',
        ],
    },
)
