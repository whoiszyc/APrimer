from __future__ import absolute_import



from setuptools import setup, find_packages
from codecs import open


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pypsa',
    version='0.14.1',
    author='Tom Brown (FIAS), Jonas Hoersch (FIAS), David Schlachtberger (FIAS)',
    author_email='brown@fias.uni-frankfurt.de',
    description='Python for Power Systems Analysis',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/PyPSA/PyPSA',
    license='GPLv3',
    packages=find_packages(exclude=['doc', 'test']),
    include_package_data=True,
    install_requires=[
        'six',
        'numpy',
        'scipy',
        'pandas>=0.19.0',
        'pyomo>=5.3',
        'matplotlib',
        'cartopy>=0.16',
        'networkx>=1.10',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ])
