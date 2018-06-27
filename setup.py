from setuptools import setup

setup(name='pymutual',
      version='0.1',
      description='Mutual API',
      url='http://github.com/kimballh/pymutual',
      author='Kimball Hill',
      author_email='me@kimball-hill.com',
      license='MIT',
      packages=['pymutual'],
      zip_safe=False,
      install_requires=[
            'requests',
            'robobrowser'
      ])
