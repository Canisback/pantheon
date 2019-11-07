from setuptools import setup, find_packages
setup(
  name = 'pantheon',
  packages = find_packages(),
  version = '1.0.7',
  description = 'Riot API library for Python and asyncio',
  author = 'Canisback',
  author_email = 'canisback@gmail.com',
  url = 'https://github.com/Canisback/pantheon',
  keywords = ['Riot API', 'python'],
  classifiers = [],
  install_requires=[
    "asyncio",
    "aiohttp"
  ],
)
