import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import click
import jinja2
import yaml
from pykwalify.core import Core

MARK = '---'


def process(template_file, author, config, input_file):
    meta = ""
    body = ""

    l = input_file.readline()
    mark = l.strip()
    if not mark == MARK:
        raise Exception(f"Invalid header. The file must start with {MARK}")

    meta = ""
    l = input_file.readline()
    while l != "" and l.strip() != mark:
        meta += l
        l = input_file.readline()

    l = input_file.readline()
    while l != "":
        body += l
        l = input_file.readline()

    basedir = Path(__file__).parent
    data = dict()
    meta_map = yaml.load(meta, Loader=yaml.FullLoader)
    Core(source_data=meta_map, schema_files=[
         str(basedir/"schemas/meta.yml")]).validate()
    data['meta'] = meta_map
    if config is not None:
        config_map = yaml.load(config, Loader=yaml.FullLoader)
        data['config'] = config_map
        Core(source_data=config_map, schema_files=[
             str(basedir/"schemas/config.yml")]).validate()
    else:
        data['config'] = dict()
    data['author'] = author
    data['basedir'] = basedir.resolve()
    data['body'] = body

    env = jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=jinja2.select_autoescape(
            enabled_extensions=('html', 'xml'),
            default_for_string=True,
        ),
        loader=jinja2.PackageLoader(__package__)
    )

    template = env.get_template(template_file)
    rendered_data = template.render(data)
    tmp_md = tempfile.NamedTemporaryFile(
        dir=".",
        mode="wt",
        prefix="doc-",
        suffix=".tmp.md",
        delete=False
    )
    tmp_md.write(rendered_data)
    tmp_md.close()

    logging.debug('---------- BEGIN RENDERED DATA ----------')
    for l in rendered_data.splitlines():
        logging.debug(l)
    logging.debug('---------- END RENDERED DATA ----------')

    tmp_tex = tempfile.NamedTemporaryFile(
        dir=".",
        mode="wt",
        prefix="doc-",
        suffix=".tmp.tex",
        delete=False
    )
    tmp_tex.close()

    logging.debug("Running pandoc")
    cmd = [
        "pandoc",
        tmp_md.name,
        "--from", "markdown+link_attributes+raw_tex",
        "-t", "latex",
        f"--resource-path", f".:{Path(__file__).parent / 'resources'}",
        "--include-in-header", basedir/"resources"/"chapter_break.tex",
        "--include-in-header", basedir/"resources"/"bullet_style.tex",
        "-V", "linkcolor:blue",
        "-V", "geometry:a4paper",
        "-V", "geometry:margin=2cm",
        "-V", "mainfont=\"IBMPlexSans\"",
        "-V", "monofont=\"IBMPlexMono\"",
        "--pdf-engine=xelatex",
        "--standalone",
        "-o", tmp_tex.name,
    ]
    res = subprocess.call(cmd)
    if res != 0:
        raise Exception("Error running Pandoc")

    logging.debug('---------- BEGIN LATEX ----------')
    with open(tmp_tex.name) as f:
        for l in f:
            logging.debug(l.strip())
    logging.debug('---------- END LATEX ----------')

    stem = Path(input_file.name).stem

    logging.debug("Running xelatex")
    with tempfile.TemporaryDirectory(dir=".") as tmp_dir:
        cmd = [
            "xelatex",
            "-halt-on-error",
            "-quiet",
            f"-output-directory={tmp_dir}",
            "-interaction=nonstopmode",
            f"-jobname={stem}",
            tmp_tex.name,
        ]

        logging.debug("Run 1")
        res = subprocess.call(cmd)
        if res != 0:
            raise Exception("Error running xelatex")

        logging.debug("Run 2")
        res = subprocess.call(cmd)
        if res != 0:
            raise Exception("Error running xelatex")

        logging.debug("Renaming PDF")
        shutil.move(Path(tmp_dir) / f"{stem}.pdf", f"{stem}.pdf")

    os.unlink(tmp_md.name)
    os.unlink(tmp_tex.name)


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

    for i in input_files:
        logging.info("Processing %s", i.name)
        config.seek(0)
        process(template_file, author, config, i)


if __name__ == "__main__":
    cli()
