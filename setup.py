from setuptools import setup, find_packages
import sivi_cnc_driver

setup(name='SiviCNCDriver',
      version=sivi_cnc_driver.__version__,
      description='A software to control my CNC',
      long_description=open('README.md').read(),
      url='http://github.com/klafyvel/SiviCNCDriver',
      author='klafyvel',
      author_email="sivigik@gmail.com",
      license='GPL',
      include_package_data=True,
      packages=find_packages(),
      install_requires= open('requirements.txt').read().split('\n'),
      classifier=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: French',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
      ],
      scripts=['bin/cnc'],
      # zip_safe=False
      )
