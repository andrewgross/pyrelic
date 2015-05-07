# #!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

if __name__ == '__main__':

    packages = find_packages(exclude=['*tests*'])

    setup(
        name="pyrelic",
        license="GPL",
        version='0.7.2',
        description=u'Python API Wrapper for NewRelic API',
        author=u'Andrew Gross',
        author_email=u'andrew.w.gross@gmail.com',
        include_package_data=True,
        url='https://github.com/andrewgross/pyrelic',
        packages=packages,
        install_requires = ["six", "requests>=2.5.0"],
        extras_require = { "tests": [
            "mock==1.0.1",
            "sure==1.2.2",
            "nose==1.2.1",
            "coverage==3.6",
            "httpretty==0.8.3"
        ]},
        classifiers=(
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Natural Language :: English',
            'Operating System :: Microsoft',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
        )
    )
