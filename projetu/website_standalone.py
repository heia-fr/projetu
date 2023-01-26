import logging
import os
import shutil
import click

from . import Projetu,ProjectType
from pathlib import Path

@click.command()
@click.option('--template', 'web_template_directory', type=click.Path(), default="web_template", help='Template')
@click.option('--author', type=str, default="PLEASE, SET AUTHOR")
@click.option('--config', type=click.File('r'), default=None)
@click.option('--type','project_type', type=click.Choice(list(map(lambda x: x.name, ProjectType))),default="ps6")
@click.option('--academic-year', 'academic_year', type=str, default="2022/2023")
@click.option('--debug/--no-debug')
@click.argument('input_files', type=click.File('r'), nargs=-1)
def cli(web_template_directory, author, config, project_type, academic_year, debug, input_files):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    p = projetu = Projetu(author,None)
    
    shutil.copytree(p.base_dir/"resources/redirect_index.html", "index.html")
    shutil.copytree(p.base_dir/web_template_directory, "web")

    base_dir = os.getcwd()
    for i in input_files:
        os.chdir(base_dir)
        path = Path(i.name)
        logging.info("Processing %s", i.name)
        rendered_data = ""
        with open(path) as f:
            try:
                rendered_data,err = projetu.read_and_inject(f, path)
                if err is not None:
                    continue 
            except Exception as e:
                logging.warn(e)
                continue
        if p.meta['type'] == project_type and p.meta['academic_year'] == academic_year:
            with open('./web/content/posts/'+projetu.encoded_url+'.md', "wt") as f:
                f.write(rendered_data.read())
            # copy image(s)
            for img in projetu.img_to_copy:
                srcImgPath = Path(os.path.join(path.parent, img))
                dstImgPath = Path(os.path.join('./web/content', projetu.encoded_url, img ))
                dstImgPath.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(srcImgPath, dstImgPath)

if __name__ == "__main__":
    cli()
