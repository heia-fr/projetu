import io
import logging
import os
import tarfile
from pathlib import Path

import click
import gitlab

from . import Projetu

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='PROJETU'
)

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--page-template', 'page_template_file', type=click.Path(), default="tb-page.md", help='Page Template')
@click.option('--template', 'template_file', type=click.Path(), default="booklet.md", help='Template')
@click.option('--config', type=click.File('r'), default=None)
@click.option('--gitlab', 'gitlab_host', type=str, default="https://gitlab.forge.hefr.ch/")
@click.option('--token', type=str, required=True)
@click.option('--project-path', type=str, required=True)
@click.option('--debug/--no-debug')
def cli(page_template_file, template_file, config, gitlab_host, token, project_path, debug):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    gl = gitlab.Gitlab(gitlab_host, private_token=token)
    projects = gl.projects.list(search=project_path, all=True)
    project: gitlab.base.RESTObject
    project_list = list()
    for project in projects:
        logging.debug("Project path : %s", project.path)
        if project.path != project_path:
            logging.warn("Bad project name : %s", project.path_with_namespace)
            continue

        print(project.http_url_to_repo)
        print(project.path_with_namespace)
        print(project.namespace['full_path'])
        logging.debug("Author : %s", project.namespace['name'])
        master = project.branches.get("master")
        commit_id = master.commit['id']

        config.seek(0)
        projetu = Projetu(page_template_file, project.namespace['name'], config)

        tar = io.BytesIO(project.repository_archive())
        tar_base = f"{project.path}-master-{commit_id}"
        logging.info("Downloading files to %s", tar_base)
        with tarfile.open(fileobj=tar) as t:
            t.extractall()
            for file in t.getmembers():
                path = Path(file.name)
                if len(path.parts) == 2 and path.suffix == ".md" and path.name != "README.md":
                    with open(path) as f:
                        try:
                            rendered_data = projetu.mark_down(f)
                            tex_file = projetu.run_pandoc(rendered_data, standalone=False)
                        except Exception as e:
                            logging.warn(e)
                            continue

                    with open(path.with_suffix('.tex'), "wt") as f:
                        f.write(tex_file.read())
                    
                    project_list.append({
                        'title': projetu.meta['titre'],
                        'path': path.parent,
                        'name': path.stem,
                        'keywords': projetu.meta['mots-clé'],
                    })

    project_list.sort(key=lambda x: x.get('title'))
    data = {
        'basedir':Path(__file__).parent,
        'projects': project_list,
    }

    template = Projetu.jinja_env.get_template(template_file)
    rendered_data = template.render(data)
    with open("booklet_2020.tex", "wt") as f:
        f.write(rendered_data)


if __name__ == "__main__":
    cli()
