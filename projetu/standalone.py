import logging

import click

from . import Projetu
from pathlib import Path

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
        stem = Path(i.name).stem
        rendered_data = p.mark_down(i)
        tex_file = p.run_pandoc(rendered_data)
        pdf_file = p.run_latex(tex_file, stem)
        logging.debug("Saving PDF")

        tex_file.seek(0)
        with open(f"{stem}.tex", "wt") as f:
            f.write(tex_file.read())


        with open(f"{stem}.pdf", "wb") as f:
            f.write(pdf_file.read())

        


if __name__ == "__main__":
    cli()
