import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djsettings',
    version='0.1',
    packages=[
        'djsettings'
    ],
    include_package_data=True,
    license='BSD License',
    description='Django app for changing settings in Admin panel.',
    long_description=README,
    url='https://github.com/miss-tais/djsettings',
    author='Taisiya Astapenko',
    author_email='taja.astapenko@gmail.com',
    install_requires=[
        'django>=2.2',
        'six'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)