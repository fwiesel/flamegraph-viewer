from setuptools import setup, find_packages

with open('requirements.txt') as requirements:
    install_requires=[ line for line in requirements]

setup(
    name='flamegraphviewer',
    version='0.1',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    extras_require={
        'redis': ['redis'],
        'hiredis': ['redis', 'hiredis'],
        'lz4': ['lz4']
    }
)
