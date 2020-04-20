import collections
import csv
import io
import logging
import os
import pickle
import tarfile
from pathlib import Path

import click
import gitlab

from . import Projetu

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='PROJETU'
)


def build_from_git(gitlab_host, token, project_path, page_template_file, config):
    gl = gitlab.Gitlab(gitlab_host, private_token=token)
    projects = gl.projects.list(search=project_path, all=True)
    project: gitlab.base.RESTObject
    project_list = list()
    for project in projects:
        logging.debug("Project path : %s", project.path)
        if project.path != project_path:
            logging.warn("Bad project name : %s", project.path_with_namespace)
            continue

        logging.debug("Author : %s", project.namespace['name'])
        master = project.branches.get("master")
        commit_id = master.commit['id']

        config.seek(0)
        projetu = Projetu(page_template_file,
                          project.namespace['name'], config)

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
                            tex_file = projetu.run_pandoc(
                                rendered_data, standalone=False)
                        except Exception as e:
                            logging.warn(e)
                            continue

                    with open(path.with_suffix('.tex'), "wt") as f:
                        f.write(tex_file.read())

                    project_list.append({
                        'path': path.parent,
                        'name': path.stem,
                        'full_path': path,
                        'author': project.namespace['name'],
                        'meta': projetu.meta
                    })

    return project_list


def build_from_cache(project_list, page_template_file, config):
    projects = collections.defaultdict(list)
    for p in project_list:
        projects[p['author']].append(p)

    for author, project_list in projects.items():
        config.seek(0)
        projetu = Projetu(page_template_file, author, config)
        for p in project_list:
            path = Path(p['full_path'].name)
            with open(path) as f:
                try:
                    rendered_data = projetu.mark_down(f)
                    tex_file = projetu.run_pandoc(
                        rendered_data, standalone=False)
                except Exception as e:
                    logging.warn(e)
                    continue

            with open(path.with_suffix('.tex'), "wt") as f:
                f.write(tex_file.read())


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--page-template', 'page_template_file', type=click.Path(), default="tb-page.md", help='Page Template')
@click.option('--template', 'template_file', type=click.Path(), default="booklet.md", help='Template')
@click.option('--config', type=click.File('r'), default=None)
@click.option('--gitlab', 'gitlab_host', type=str, default="https://gitlab.forge.hefr.ch/")
@click.option('--token', type=str, required=True)
@click.option('--project-path', type=str, required=True)
@click.option('--output', type=str, default="booklet-2020")
@click.option('--filter', 'project_filter', type=click.File(), default=None)
@click.option('--debug/--no-debug')
@click.option('--from-cache/--no-from-cache')
def cli(page_template_file, template_file, config, gitlab_host, token, project_path, output, project_filter, debug, from_cache):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if from_cache:
        project_list = build_from_git(
            gitlab_host, token, project_path, page_template_file, config)
        with open(Path(output).with_suffix(".pickle"), "wb") as f:
            pickle.dump(project_list, f)
    else:
        with open(Path(output).with_suffix(".pickle"), "rb") as f:
            project_list = pickle.load(f)
        build_from_cache(project_list, page_template_file, config)

    def clean_list(l):
        if l is None:
            return []
        return [i for i in l if i is not None]

    project_list.sort(key=lambda x: x['meta']['titre'])

    if project_filter is not None:
        filter_map = dict()
        projects_reader = csv.reader(project_filter)
        projects_reader.__next__()  # skip header
        for row in projects_reader:
            filter_map[(row[1], row[2])] = True
        print(filter_map)
        project_list = [i for i in project_list if (
            i['name'], i['author']) in filter_map]

    data = {
        'basedir': Path(__file__).parent,
        'projects': project_list,
    }

    with open(Path(output).with_suffix(".csv"), 'w', newline='') as csvfile:
        projects_writer = csv.writer(csvfile)
        projects_writer.writerow([
            'path',
            'name',
            'professeur',
            'titre',
            'filières',
            'orientations',
            'langue',
            'professeurs co-superviseurs',
            'assistants',
            'attribué à',
        ])

        for p in project_list:
            projects_writer.writerow([
                p['path'],
                p['name'],
                p['author'],
                p['meta']['titre'],
                ", ".join(clean_list(p['meta'].get('filières', []))),
                ", ".join(clean_list(p['meta'].get('orientations', []))),
                ", ".join(clean_list(p['meta'].get('langue', []))),
                ", ".join(clean_list(p['meta'].get(
                    'professeurs co-superviseurs', []))),
                ", ".join(clean_list(p['meta'].get('assistants', []))),
                ", ".join(clean_list(p['meta'].get('attribué à', []))),
            ])

    template = Projetu.jinja_env.get_template(template_file)
    rendered_data = template.render(data)
    with open(Path(output).with_suffix(".tex"), "wt") as f:
        f.write(rendered_data)


if __name__ == "__main__":
    cli()
