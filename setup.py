from distutils.core import setup
from setuptools import find_packages

setup(name='retcon',
      version='0.1',
      author='iWeb',
      author_email='sg@iweb.co.uk',
      url='https://github.com/iwebhosting/retcon',
      description="Retcon",
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      scripts=['bin/retcon'],
      install_requires = [l.strip() for l in open('requirements.txt').readlines()],
      package_data={'retcon': [
        'templates/*.html',
        'static/*',
      ]},
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                  ],
     )
