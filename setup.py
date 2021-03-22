from setuptools import setup, find_packages

from os import path
this_directory = path.dirname(__file__)
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()



setup(
  name = 'pantheon',
  packages = find_packages(),
  version = '1.3.0',
  description = 'Riot API library for Python and asyncio',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Canisback',
  author_email = 'canisback@gmail.com',
  url = 'https://github.com/Canisback/pantheon',
  keywords = ['Riot API', 'python'],
  classifiers = [],
  install_requires=[
    "aiohttp"
  ],
)
