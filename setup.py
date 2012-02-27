
from setuptools import setup, find_packages

REQUIREMENTS = (
    'django>=1.3',
)

TEST_REQUIREMENTS = ('mock',)

from web_utils import VERSION

setup(
    name="django-web-utils",
    version=VERSION,
    author="Aaron Madison",
    description="Django helpers for working with the web.",
    long_description=open('README', 'r').read(),
    url="https://github.com/madisona/django-web-utils",
    packages=find_packages(exclude=["example"]),
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
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
