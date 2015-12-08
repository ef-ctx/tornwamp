from setuptools import setup, find_packages


README = open('README.rst').read()


setup(name="tornwamp",
      author="Tatiana Al-Chueyr Martins",
      author_email="tatiana.alchueyr@gmail.com",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
      download_url = 'http://pypi.python.org/pypi/tornwamp',
      description=u"WAMP (Web Application Messaging Protocol) utilities",
      include_package_data=True,
      install_requires=["tornado>=4.0", "enum34"],
      license="GNU GPLv2",
      long_description=README,
      packages=find_packages(),
      tests_require=["coverage==3.6", "nose==1.2.1", "pep8==1.4.1", "mock==1.0.1", "pylint==1.0.0"],
      url = "http://github.com/ef-ctx/tornwamp",
      version="1.0.1"
)
