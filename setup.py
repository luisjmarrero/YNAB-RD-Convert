from setuptools import setup, find_packages

setup(
    name='ynab-convert-rd',
    version='1.0.0',
    description='Convert Dominican bank files to YNAB CSV format',
    author='Luis Marrero',
    packages=find_packages(include=['ynab_convert_rd', 'ynab_convert_rd.*', 'converters', 'converters.*']),
    install_requires=[
        'colorlog',
    ],
    entry_points={
        'console_scripts': [
            'ynab-convert-rd=ynab_convert_rd.main:main',
        ],
    },
    python_requires='>=3.7',
)
