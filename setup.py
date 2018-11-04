from setuptools import setup, find_packages

setup(name='pymutual',
      version='0.1',
      description='Mutual API',
      url='http://github.com/kimballh/pymutual',
      packages=find_packages(),
      author='Kimball Hill',
      author_email='me@kimball-hill.com',
      license='MIT',
      zip_safe=False,
      install_requires=[
            'requests',
            'robobrowser'
      ])
