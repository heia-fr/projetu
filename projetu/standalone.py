import logging

import click

from . import Projetu


@click.command()
@click.option('--template', 'template_file', type=click.Path(), default="project.md", help='Template')
@click.option('--author', type=str, default="PLEASE, SET AUTHOR")
@click.option('--config', type=click.File('r'), default=None)
@click.option('--debug/--no-debug')
@click.argument('input_files', type=click.File('r'), nargs=-1)
def cli(template_file, author, config, debug, input_files):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    p = Projetu(template_file, author, config)

    for i in input_files:
        logging.info("Processing %s", i.name)
        p.process(i)


if __name__ == "__main__":
    cli()
