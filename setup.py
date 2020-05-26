from setuptools import setup

setup(
    name='kfk',
    version='0.1',
    py_modules=['kfk_cli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        kfk=kfk_cli:kfk
    ''',
)