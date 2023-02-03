from setuptools import find_packages, setup

setup(
    name='projetu',
    version='0.2.0',
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
        'resources/*',
        'schemas/*',
        'web_template/*',
        'web_template/*/*',
        'web_template/*/*/*',
        'web_template/*/*/*/*',
        'web_template/*/*/*/*/*',
        'web_template/*/*/*/*/*/*',
        'web_template/*/*/*/*/*/*/*',
        'web_template/*/*/*/*/*/*/*/*',
        'web_template/*/*/*/*/*/*/*/*/*'
    ]},
    zip_safe=False,
    entry_points='''
        [console_scripts]
        projetu-tag=projetu.tag_projects:cli
        projetu-create-subgroup=projetu.create_subgroups:cli
        projetu-website-global=projetu.website_global:cli
        projetu-website-standalone=projetu.website_standalone:cli
    ''',
)
