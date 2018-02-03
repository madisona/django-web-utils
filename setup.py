
from setuptools import setup, find_packages

from web_utils import VERSION

setup(
    name="django-web-utils",
    version=VERSION,
    author="Aaron Madison",
    description="Django helpers for working with the web.",
    long_description=open('README', 'r').read(),
    url="https://github.com/madisona/django-web-utils",
    packages=find_packages(exclude=["example"]),
    include_package_data=True,
    install_requires=open('requirements/requirements.txt').read().split('\n'),
    tests_require=open('requirements/test.txt').read().split('\n'),
    zip_safe=False,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
