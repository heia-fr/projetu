from setuptools import find_packages, setup

setup(
    name='projetu',
    version='0.0.2',
    description='Student Project Description Generator',
    install_requires=[
        'Click',
        'Jinja2',
        'MarkupSafe',
        'PyYAML'
    ],
    packages=find_packages(),
    package_data={'projetu': [
        'templates/*',
        'resources/*'
    ]},
    zip_safe=False,
    entry_points='''
        [console_scripts]
        projetu=projetu:cli
    ''',
)
