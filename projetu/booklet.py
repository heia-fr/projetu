import collections
import csv
import io
import logging
import os
import pickle
import tarfile
from pathlib import Path
import yaml
from enum import Enum,unique

import click
import gitlab

from . import Projetu

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='PROJETU'
)

@unique
class ProjectType(Enum):
    ps5 = "Projet de semestre 5"
    ps6 = "Projet de semestre 6"
    tb = "Projet de bachelor"

def build_from_git(gitlab_host, token, project_type, school_year, profs_list, page_template_file, config):
    gl = gitlab.Gitlab(gitlab_host, private_token=token)
    project_list = list()
    main_group = gl.groups.get(3063)
    subgroups = main_group.subgroups.list()
    for sg in subgroups:
        prof = ""
        subgroup = gl.groups.get(sg.id)
        for m in subgroup.members.list():
            if m.access_level == gitlab.const.MAINTAINER_ACCESS:
                prof = m.username
        if prof=="":
            logging.warn(f"No maintainer found for group: {subgroup.full_path}")
            continue
        projects = subgroup.projects.list()
        project: gitlab.base.RESTObject
        for gp in projects:
            project = gl.projects.get(gp.id)
            logging.info("Project path : %s", project.path)
            logging.debug("Author : %s", prof)
            try:
                branch = project.branches.get(project.default_branch)
            except Exception as e:
                logging.error(e)
                continue

            commit_id = branch.commit['id']
            if config!=None:
                config.seek(0)
            projetu = Projetu(page_template_file,
                            project.namespace['name'], config)

            tar = io.BytesIO(project.repository_archive())
            tar_base = f"{project.path}-{project.default_branch}-{commit_id}"
            logging.info("Downloading files to %s", tar_base)
            with tarfile.open(fileobj=tar) as t:
                t.extractall()
                for file in t.getmembers():
                    path = Path(file.name)
                    if len(path.parts) >= 2 and path.suffix == ".md" and path.name != "README.md":
                        with open(path) as f:
                            try:
                                rendered_data = projetu.mark_down(f)
                                tex_file = projetu.run_pandoc(
                                    rendered_data, standalone=False)
                            except Exception as e:
                                logging.warn(e)
                                continue
                        if projetu.meta['type'] == ProjectType[project_type].value and projetu.meta['school_year'] == school_year:
                            with open(path.with_suffix('.tex'), "wt") as f:
                                f.write(tex_file.read())

                            project_list.append({
                                'path': path.parent,
                                'name': path.stem,
                                'full_path': path,
                                'author': prof,
                                'meta': projetu.meta
                            })
                        else:
                            logging.info(f"Project \"{projetu.meta['title']}\" not included. Type: {projetu.meta['type']} - {projetu.meta['school_year']}")
    return project_list


def build_from_cache(project_list, page_template_file, config):
    projects = collections.defaultdict(list)
    for p in project_list:
        projects[p['author']].append(p)

    for author, project_list in projects.items():
        config.seek(0)
        projetu = Projetu(page_template_file, author, config)
        for p in project_list:
            path = Path(p['full_path'])
            with open(path) as f:
                try:
                    print(p['meta'])
                    rendered_data = projetu.mark_down(f, meta_map=p['meta'])
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
@click.option('--config', type=click.File('r'))
@click.option('--gitlab', 'gitlab_host', type=str, default="https://gitlab.forge.hefr.ch/")
@click.option('--token', type=str, required=True)
@click.option('--profs', type=click.File('r'), default=None)
@click.option('--type','project_type', type=click.Choice(list(map(lambda x: x.name, ProjectType))),default="tb")
@click.option('--school-year', 'school_year', type=str, default="2021/2022")
@click.option('--output', type=str, default="booklet_2020")
@click.option('--filter', 'project_filter', type=click.File(), default=None)
@click.option('--debug/--no-debug')
@click.option('--from-cache/--no-from-cache')
def cli(page_template_file, template_file, config, gitlab_host, token, profs, project_type, school_year, output, project_filter, debug, from_cache):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    profs_list = None
    if profs is not None:
        profs_list = yaml.load(profs, Loader=yaml.FullLoader)

    if from_cache:
        with open(Path(output).with_suffix(".pickle"), "rb") as f:
            project_list = pickle.load(f)
        build_from_cache(project_list, page_template_file, config)
    else:
        project_list = build_from_git(
            gitlab_host, token, project_type, school_year, profs_list, page_template_file, config)
        with open(Path(output).with_suffix(".pickle"), "wb") as f:
            pickle.dump(project_list, f)

    def clean_list(l):
        if l is None:
            return []
        return [i for i in l if i is not None]

    project_list.sort(key=lambda x: x['meta']['title'].upper())

    if project_filter is not None:
        filter_map = dict()
        projects_reader = csv.DictReader(project_filter)
        for row in projects_reader:
            filter_map[(row['name'], row[PROFESSEUR])] = row
        logging.debug(filter_map)
        filtered_list = list()
        done_keys = set()
        for p in project_list:
            key = (p['name'], p['author'])
            if key in filter_map:
                done_keys.add(key)
                item = filter_map[key]
                logging.info("Adding project : %s (%s)", key[0], key[1])
                students = [x.strip() for x in item[ATTRIBUE_A].split(",")]
                if not ATTRIBUE_A in p['meta']:
                    p['meta'][ATTRIBUE_A] = list()
                if p['meta'][ATTRIBUE_A] != students:
                    logging.info("Fixing attribution : %s -> %s", p['meta'][ATTRIBUE_A], students)
                    p['meta'][ATTRIBUE_A] = students
                filtered_list.append(p)

        for key in filter_map.keys():
            if not key in done_keys:
                logging.error("KEY %s not found in project list", key)

        project_list = filtered_list
        build_from_cache(project_list, page_template_file, config)

    data = {
        'basedir': Path(__file__).parent,
        'projects': project_list,
        'project_type': ProjectType[project_type].value,
        'school_year': school_year
    }

    with open(Path(output).with_suffix(".csv"), 'w', newline='') as csvfile:
        projects_writer = csv.writer(csvfile)
        projects_writer.writerow([
            'path',
            'name',
            'professor',
            'title',
            'departments',
            'orientations',
            'languages',
            'max_students',
            'professors',
            'assistants',
            'assigned_to',
        ])

        
        for p in project_list:
            # print(p)
            projects_writer.writerow([
                p['path'],
                p['name'],
                p['author'],
                p['meta']['title'],
                ", ".join(clean_list(p['meta'].get('departments', []))),
                ", ".join(clean_list(p['meta'].get('orientations', []))),
                ", ".join(clean_list(p['meta'].get('languages', []))),
                p['meta']['max_students'],
                ", ".join(clean_list(p['meta'].get('professors', []))),
                ", ".join(clean_list(p['meta'].get('assistants', []))),
                ", ".join(clean_list(p['meta'].get('assigned_to', []))),
            ])

    template = Projetu.jinja_env.get_template(template_file)
    rendered_data = template.render(data)
    with open(Path(output).with_suffix(".tex"), "wt") as f:
        f.write(rendered_data)


if __name__ == "__main__":
    cli()
