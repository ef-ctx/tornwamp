from setuptools import setup, find_packages


README = open('README.rst').read()


setup(name="tornwamp",
      author="Tatiana Al-Chueyr Martins",
      author_email="tatiana.alchueyr@gmail.com",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
        ],
      download_url = 'http://pypi.python.org/pypi/tornwamp',
      description=u"WAMP (Web Application Messaging Protocol) utilities",
      include_package_data=True,
      install_requires=["greenlet==0.4.9", "greenlet_tornado==1.1.3", "tornado>=4.0", "enum34", "tornadis==0.8.0", "six==1.10.0", "deprecated==1.2.5"],
      license="Apache License",
      long_description=README,
      packages=find_packages(),
      tests_require=["coverage==4.0.3", "nose==1.3.7", "pep8==1.7.0", "mock==1.0.1", "pylint==1.5.4"],
      url = "http://github.com/ef-ctx/tornwamp",
      version="2.1.0"
)
