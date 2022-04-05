import logging
import os

import click

from . import Projetu,ProjectType
from pathlib import Path

@click.command()
@click.option('--template', 'template_file', type=click.Path(), default="project.md", help='Template')
@click.option('--author', type=str, default="PLEASE, SET AUTHOR")
@click.option('--config', type=click.File('r'), default=None)
@click.option('--type','project_type', type=click.Choice(list(map(lambda x: x.name, ProjectType))),default="tb")
@click.option('--academic-year', 'academic_year', type=str, default="2021/2022")
@click.option('--debug/--no-debug')
@click.argument('input_files', type=click.File('r'), nargs=-1)
def cli(template_file, author, config, project_type, academic_year, debug, input_files):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    p = Projetu(template_file, author, config)

    base_dir = os.getcwd()
    for i in input_files:
        os.chdir(base_dir)
        os.chdir(Path(i.name).parent.absolute())
        logging.info("Processing %s", i.name)
        stem = Path(i.name).stem
        rendered_data,err = p.mark_down(i)
        if err is not None:
            continue
        if p.meta['type'] == project_type and p.meta['academic_year'] == academic_year:
            tex_file = p.run_pandoc(rendered_data)
            pdf_file = p.run_latex(tex_file, stem)
            logging.debug("Saving PDF")

            tex_file.seek(0)
            with open(f"{stem}.tex", "wt") as f:
                f.write(tex_file.read())

            with open(f"{base_dir}/{stem}.pdf", "wb") as f:
                f.write(pdf_file.read())

        


if __name__ == "__main__":
    cli()
