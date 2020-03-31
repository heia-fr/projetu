from setuptools import find_packages, setup

setup(
    name='projetu',
    version='0.0.3',
    description='Student Project Description Generator',
    install_requires=[
        'Click',
        'Jinja2',
        'MarkupSafe',
        'pykwalify',
        'PyYAML',
    ],
    packages=find_packages(),
    package_data={'projetu': [
        'templates/*',
        'resources/*',
        'schemas/*',
    ]},
    zip_safe=False,
    entry_points='''
        [console_scripts]
        projetu=projetu:cli
    ''',
)
