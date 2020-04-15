from setuptools import find_packages, setup

setup(
    name='projetu',
    version='0.1.0',
    description='Student Project Description Generator',
    install_requires=[
        'Click',
        'gitpython',
        'Jinja2',
        'MarkupSafe',
        'python-gitlab',
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
        projetu=projetu.standalone:cli
        projetu-book=projetu.booklet:cli
    ''',
)
