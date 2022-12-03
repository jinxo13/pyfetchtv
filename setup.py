import os
import re
from setuptools import find_packages, setup


READMEFILE = "README.md"
VERSIONFILE = os.path.join("pyfetchtv", "_version.py")
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"


def get_version():
    verstrline = open(VERSIONFILE, "rt").read()
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError(
            "Unable to find version string in %s." % VERSIONFILE)


setup(
    name='pyfetchtv',
    version=get_version(),
    description='FetchTV library',
    long_description=open(READMEFILE).read(),
    url='http://git.local/git/pyfetchtv',
    author='Hamish McNeish',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'jsonpath-ng>=1.5.3',
        'websocket-client>=1.3.2',
        'python-dotenv>=0.20.0',
        'fuzzy_match>=0.0.1',
        'numpy>=1.21.1'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        ],
)
