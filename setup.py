#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages

setup(name="IMAP4PowerToy",
      version="0.2dev",
      description="IMAP4 Power Toy",
      author="Nick Fisher",
      packages = find_packages(),
      zip_safe = True,
      entry_points = {
          'console_scripts': [
              'impty = impty.tool:main',
          ]
      }
     )
