import io
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import jinja2
import yaml
from pykwalify.core import Core

logger = logging.getLogger(__name__)

MARK = '---'


@dataclass
class Projetu:
    template_file: str
    author: str
    config_file: io.FileIO
    base_dir: Path = field(init=False)
    config_map: dict = field(init=False)
    meta: dict = field(init=False)

    jinja_env = jinja2.Environment(
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

    def __post_init__(self):
        logger.debug("Post Init")
        self.base_dir = Path(__file__).parent
        self.config_map = dict()
        if self.config_file is not None:
            self.config_map = yaml.load(
                self.config_file, Loader=yaml.FullLoader)
            print(self.config_file)
            Core(source_data=self.config_map, schema_files=[
                str(self.base_dir/"schemas/config.yml")]).validate()

    def mark_down(self, input_file):
        meta = ""
        body = ""

        logger.debug("Building markdown for %s", input_file)
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

        data = dict()
        meta_map = yaml.load(meta, Loader=yaml.FullLoader)
        self.meta = meta_map
        logger.debug(meta)
        Core(source_data=meta_map, schema_files=[
            str(self.base_dir/"schemas/meta_v1.yml")]).validate()

        data['meta'] = meta_map
        data['config'] = self.config_map
        data['author'] = self.author
        data['basedir'] = self.base_dir.resolve()
        data['body'] = body

        template = Projetu.jinja_env.get_template(self.template_file)
        rendered_data = template.render(data)

        logger.debug('---------- BEGIN RENDERED DATA ----------')
        for l in rendered_data.splitlines():
            logger.debug(l)
        logger.debug('---------- END RENDERED DATA ----------')

        return io.StringIO(rendered_data)

    def run_pandoc(self, markdown, tmp_dir=".", standalone=True):

        tmp_md = tempfile.NamedTemporaryFile(
            dir=tmp_dir,
            mode="wt",
            prefix="doc-",
            suffix=".tmp.md",
            delete=False
        )
        tmp_md.write(markdown.read())
        tmp_md.close()

        tmp_tex = tempfile.NamedTemporaryFile(
            dir=tmp_dir,
            mode="wt",
            prefix="doc-",
            suffix=".tmp.tex",
            delete=False
        )
        tmp_tex.close()

        logger.debug("Running pandoc")
        cmd = [
            "pandoc",
            tmp_md.name,
            "--from", "markdown+link_attributes+raw_tex",
            "-t", "latex",
            f"--resource-path", f".:{Path(__file__).parent / 'resources'}",
            "-V", "linkcolor:blue",
            "-V", "geometry:a4paper",
            "-V", "geometry:margin=2cm",
            "-V", "mainfont=\"IBMPlexSans\"",
            "-V", "monofont=\"IBMPlexMono\"",
            "--id-prefix=abcdef",
            "--pdf-engine=xelatex",
            "-o", tmp_tex.name,
        ]
        if standalone:
            cmd += [
                "--include-in-header", self.base_dir/"resources"/"wrapfig.tex",
                "--include-in-header", self.base_dir/"resources"/"silence.tex",
                "--include-in-header", self.base_dir/"resources"/"chapter_break.tex",
                "--include-in-header", self.base_dir/"resources"/"bullet_style.tex",
                "--standalone",
            ]

        res = subprocess.call(cmd)
        if res != 0:
            raise Exception("Error running Pandoc")

        os.unlink(tmp_md.name)

        logger.debug('---------- BEGIN LATEX ----------')
        with open(tmp_tex.name) as f:
            for l in f:
                logger.debug(l.strip())
        logger.debug('---------- END LATEX ----------')

        with open(tmp_tex.name) as f:
            res = io.StringIO(f.read())
        os.unlink(tmp_tex.name)

        return res

    def run_latex(self, tex_file, stem, directory="."):
        logger.debug("Running xelatex")

        tmp_tex = tempfile.NamedTemporaryFile(
            dir=directory,
            mode="wt",
            prefix="doc-",
            suffix=".tmp.tex",
            delete=False
        )
        tmp_tex.write(tex_file.read())
        tmp_tex.close()

        with tempfile.TemporaryDirectory(dir=directory) as tmp_dir:
            cmd = [
                "xelatex",
                "-halt-on-error",
                f"-output-directory={tmp_dir}",
                "-interaction=batchmode",
                f"-jobname={stem}",
                tmp_tex.name,
            ]

            for i in range(2):
                logger.debug(f"Run {i}")
                res = subprocess.call(cmd)
                if res != 0:
                    logger.error("Error processing tex file")
                    logger.error('---------- BEGIN LATEX ----------')
                    with open(tmp_tex.name) as f:
                        for line, l in enumerate(f):
                            logger.error("TEX %5d > %s", line, l.strip())
                    logger.error('---------- END LATEX ----------')
                    logger.error('---------- BEGIN LOG ----------')
                    with open(Path(tmp_dir)/f"{stem}.log") as f:
                        for line, l in enumerate(f):
                            logger.error("LOG %5d > %s", line, l.strip())
                    logger.error('---------- END LOG ----------')
                    raise Exception("Error running xelatex")

            os.unlink(tmp_tex.name)
            with open(Path(tmp_dir) / f"{stem}.pdf", "rb") as f:
                return io.BytesIO(f.read())
