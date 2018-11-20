from setuptools import find_packages, setup

version = '1.0.0'

setup(
    name='chunk_logger',
    version=version,
    description="SafeTimedChunksFileHandler",
    long_description=
    """SafeTimedChunksFileHandler is concurrent safe FileHandler that splits logs into N-minute chunks""",
    author='Alexander Zelenin',
    author_email='az@inten.to',
    url='https://github.com/intento/chunk_logger',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'old*']),
    zip_safe=False,
    install_requires=[])
