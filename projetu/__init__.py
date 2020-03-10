import os
import tempfile
from pathlib import Path

import click
import jinja2
import yaml
import subprocess
import shutil

MARK = '---'

@click.command()
@click.option('--template', 'template_file', type=click.Path(), default="project.md", help='Template')
@click.argument('input_file', type=click.File('r'))
def cli(template_file, input_file):
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
    data = yaml.load(meta, Loader=yaml.FullLoader)
    data['basedir'] = basedir.resolve()
    data['body'] = body

    env = jinja2.Environment(
        autoescape=jinja2.select_autoescape(
            enabled_extensions=('html', 'xml'),
            default_for_string=True,
        ),
        loader=jinja2.PackageLoader(__package__)
    )

    template = env.get_template(template_file)
    tmp_md = tempfile.NamedTemporaryFile(
        dir=".",
        mode="wt",
        prefix="doc-",
        suffix=".tmp.md",
        delete=False
    )
    tmp_md.write(template.render(data))
    tmp_md.close()

    tmp_tex = tempfile.NamedTemporaryFile(
        dir=".",
        mode="wt",
        prefix="doc-",
        suffix=".tmp.tex",
        delete=False
    )
    tmp_tex.close()

    cmd=[
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
    subprocess.call(cmd)

    stem = Path(input_file.name).stem

    with tempfile.TemporaryDirectory(dir=".") as tmp_dir:
        cmd=[
            "xelatex",
            "-halt-on-error",
            f"-output-directory={tmp_dir}",
            "-interaction=batchmode",
            f"-jobname={stem}",
            tmp_tex.name,
        ]

        subprocess.call(cmd)
        subprocess.call(cmd)
        
        shutil.move(Path(tmp_dir) / f"{stem}.pdf", f"{stem}.pdf")

    os.unlink(tmp_md.name)
    os.unlink(tmp_tex.name)

if __name__ == "__main__":
    cli()
