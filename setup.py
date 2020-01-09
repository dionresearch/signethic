import io
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

with io.open(os.path.join(here, 'VERSION')) as f:
    version = f.read()

requirements = ['pycryptodome==3.9.4']

setup(name='signethic',
      version=version,
      entry_points={
          'console_scripts': [
              'signethic=signethic.__init__:main',
          ],
      },
      install_requires=requirements,
      include_package_data=True,
      description='Object signing and signature verification module',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/dionresearch/signethic',
      author='Francois Dion',
      author_email='fdion@dionresearch.com',
      license='MIT',
      packages=['signethic'],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
)

