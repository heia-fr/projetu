import codecs
import collections
import csv
import io
import logging
import os
import pickle
from re import sub
import tarfile
from pathlib import Path
import yaml
import hashlib
import shutil

import yaml
from yaml.loader import SafeLoader

import click
import gitlab

from . import Projetu,ProjectType

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='PROJETU'
)

def get_projects_recursive(gitlab_instance, group, prof, project_type, academic_year,output_directory,tag=None,update_assignations=None):
    project_list = list()
    subgroups = group.subgroups.list(all=True)
    for sg in subgroups:
        project_list+=get_projects_recursive(gitlab_instance,gitlab_instance.groups.get(sg.id),prof, project_type, academic_year,output_directory,tag)
    projects = group.projects.list(all=True)
    project: gitlab.base.RESTObject
    for gp in projects:
        project = gitlab_instance.projects.get(gp.id)
        logging.info("Project path : %s", project.path)
        logging.debug("Author : %s", prof)
        try:
            if tag is not None:
                taginfo = project.tags.get(id=tag)
                commit_id = taginfo.commit['id']
            else:
                branch = project.branches.get(project.default_branch)
                commit_id = branch.commit['id']
        except Exception as e:
            logging.error(e)
            continue

        projetu = Projetu(prof,None)
        tar = io.BytesIO(project.repository_archive(sha=commit_id))
        tar_base = f"{project.path}-{project.default_branch}-{commit_id}"
        logging.info("Downloading files to %s", tar_base)
        with tarfile.open(fileobj=tar) as t:
            t.extractall()
            for file in t.getmembers():
                path = Path(file.name)
                rendered_data = ""
                if len(path.parts) >= 2 and path.suffix == ".md" and path.name != "README.md":
                    with open(path) as f:
                        try:
                            key = str(path.parent) + path.stem
                            update_assignation = None
                            if update_assignations is not None and key in update_assignations:
                                update_assignation = update_assignations[key]
                            rendered_data,err = projetu.read_and_inject(f, path, update_assignation)
                            if err is not None:
                                continue 
                        except Exception as e:
                            logging.warn(e)
                            continue
                    if projetu.meta['type'] == project_type and projetu.meta['academic_year'] == academic_year:
                        with open(output_directory+'/content/posts/'+projetu.encoded_url+'.md', "wt") as f:
                            f.write(rendered_data.read())
                        # copy image(s)
                        for img in projetu.img_to_copy:
                            srcImgPath = Path(os.path.join(path.parent, img))
                            dstImgPath = Path(os.path.join(output_directory, 'content', projetu.encoded_url, img ))
                            dstImgPath2 = Path(os.path.join(output_directory, 'content', img ))
                            dstImgPath.parent.mkdir(parents=True, exist_ok=True)
                            dstImgPath2.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy(srcImgPath, dstImgPath)
                            shutil.copy(srcImgPath, dstImgPath2)
                        project_list.append({
                            'path': path.parent,
                            'name': path.stem,
                            'full_path': path,
                            'author': prof,
                            'meta': projetu.meta
                        })
                    else:
                        logging.info(f"Project \"{projetu.meta['title']}\" not included. Type: {projetu.meta['type']} - {projetu.meta['academic_year']}")
    return project_list


def build_from_git(gitlab_host, token, project_type, academic_year, profs_list, output_directory, tag=None, update_assignations=None):
    gl = gitlab.Gitlab(gitlab_host, private_token=token)
    project_list = list()
    main_group = gl.groups.get(3063)
    subgroups = main_group.subgroups.list(all=True)
    for sg in subgroups:
        prof = ""
        subgroup = gl.groups.get(sg.id)
        for m in subgroup.members.list(all=True):
            if m.access_level == gitlab.const.MAINTAINER_ACCESS:
                prof = m.name
        if prof=="":
            logging.warn(f"No maintainer found for group: {subgroup.full_path}")
            continue
        project_list+=get_projects_recursive(gl, subgroup, prof, project_type, academic_year, output_directory, tag, update_assignations)
    return project_list


def build_expert_from_cache(project_list, config, updated_assignation):
    projects = collections.defaultdict(list)
    for p in project_list:
        projects[p['author']].append(p)
    all_projects = []
    for author, project_list in projects.items():
        if config!=None:
            config.seek(0)
        projetu = Projetu(author, config)
        for p in project_list:
            key = str(p['path'])+p['name']
            if key in updated_assignation:
                p['meta']['assigned_to'] = [updated_assignation[key]]
            elif not 'assigned_to' in p['meta']:
                continue
            path = Path(p['full_path'])
            with open(path) as f:
                try:
                    rendered_data,err = projetu.mark_down(f, meta_map=p['meta'])
                    if err is not None:
                        continue
                    tex_file = projetu.run_pandoc(
                        rendered_data, standalone=False)
                except Exception as e:
                    logging.warn(e)
                    continue

            with open(path.with_suffix('.tex'), "wt") as f:
                f.write(tex_file.read())
            all_projects.append(p)
    return all_projects


def build_from_cache(project_list, config):
    projects = collections.defaultdict(list)
    for p in project_list:
        projects[p['author']].append(p)

    for author, project_list in projects.items():
        if config!=None:
            config.seek(0)
        projetu = Projetu(author, config)
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
@click.option('--template', 'web_template_directory', type=click.Path(), default="web_template", help='Template')
@click.option('--config', type=click.File('r'))
@click.option('--gitlab', 'gitlab_host', type=str, default="https://gitlab.forge.hefr.ch/")
@click.option('--token', type=str, required=True)
@click.option('--profs', type=click.File('r'), default=None)
@click.option('--type','project_type', type=click.Choice(list(map(lambda x: x.name, ProjectType))),default="tb")
@click.option('--school-year', 'academic_year', type=str, default="2021/2022")
@click.option('--output', type=str, default="booklet_2020")
@click.option('--filter', 'project_filter', type=click.File(), default=None)
@click.option('--debug/--no-debug')
@click.option('--from-cache/--no-from-cache')
@click.option('--update-assignations', 'update_assignations', type=str, default=None)
@click.option('--output-directory', 'output_directory', type=str, default="web")
@click.option('--tag', type=str, default=None)
@click.option('--secret',type=str, default="secret")
def cli(web_template_directory, config, gitlab_host, token, profs, project_type, academic_year, output, project_filter, debug, from_cache,tag, update_assignations,output_directory,secret):
    # copy website_template to a web dir in current directpry
    p = projetu = Projetu("",None)
    base_dir = p.base_dir
    shutil.copytree(base_dir/web_template_directory, output_directory)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config_datas = []
    with open(output_directory+'/config.yaml') as f:
        config_datas = yaml.load(f, Loader=SafeLoader)
    config_datas['title'] = ProjectType[project_type].value+' - '+academic_year
    with open(output_directory+'/config.yaml', 'w') as f:
        yaml.dump(config_datas, f)
    
    if tag is not None and tag.lower()=="none":
        tag=None

    update_assignations_datas = None
    if update_assignations is not None:
        logging.info("Update assignation not null")
        with open(Path(update_assignations), "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            update_assignations_datas = {}
            nb = 0
            for r in reader:
                nb+=1
                if nb>2 and r[14]!="" and r[15]!="":
                    logging.info("Add assignation to update")
                    update_assignations_datas[r[0]+r[1]] = r[14]+" "+r[15]
    
    profs_list = None
    if profs is not None:
        profs_list = yaml.load(profs, Loader=yaml.FullLoader)

    if from_cache:
        with open(Path(output).with_suffix(".pickle"), "rb") as f:
            project_list = pickle.load(f)
        if update_assignations is None:
            build_from_cache(project_list, config)
        else:
            project_list = build_expert_from_cache(project_list, config, updated_assignation=update_assignations_datas)
    else:
        project_list = build_from_git(
            gitlab_host, token, project_type, academic_year, profs_list, output_directory, tag, update_assignations_datas)
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
            filter_map[(row['name'], row['author'])] = row
        logging.debug(filter_map)
        filtered_list = list()
        done_keys = set()
        for p in project_list:
            key = (p['name'], p['author'])
            if key in filter_map:
                done_keys.add(key)
                item = filter_map[key]
                logging.info("Adding project : %s (%s)", key[0], key[1])
                students = [x.strip() for x in item['assigned_to'].split(",")]
                if not 'assigned_to' in p['meta']:
                    p['meta']['assigned_to'] = list()
                if p['meta']['assigned_to'] != students:
                    logging.info("Fixing attribution : %s -> %s", p['meta']['assigned_to'], students)
                    p['meta']['assigned_to'] = students
                filtered_list.append(p)

        for key in filter_map.keys():
            if not key in done_keys:
                logging.error("KEY %s not found in project list", key)

        project_list = filtered_list
        build_from_cache(project_list, config)

    data = {
        'basedir': Path(__file__).parent,
        'projects': project_list,
        'project_type': ProjectType[project_type].value,
        'academic_year': academic_year
    }

    with open(Path(output).with_suffix(".csv"), mode='w', encoding='utf-8-sig', newline='') as csvfile:
        projects_writer = csv.writer(csvfile)
        projects_writer.writerow([
            'path',
            'name',
            'professor',
            'title',
            'continuation',
            'confidential',
            'departments',
            'orientations',
            'languages',
            'max_students',
            'professors',
            'assistants',
            'assigned_to',
            'weight',
        ])

        
        for p in project_list:
            # print(p)
            projects_writer.writerow([
                p['path'],
                p['name'],
                p['author'],
                p['meta']['title'],
                p['meta']['continuation'],
                p['meta']['confidential'],
                ", ".join(clean_list(p['meta'].get('departments', []))),
                ", ".join(clean_list(p['meta'].get('orientations', []))),
                ", ".join(clean_list(p['meta'].get('languages', []))),
                p['meta']['max_students'],
                ", ".join(clean_list(p['meta'].get('professors', []))),
                ", ".join(clean_list(p['meta'].get('assistants', []))),
                ", ".join(clean_list(p['meta'].get('assigned_to', []))),
                p['meta']['weight'] if "weight" in p['meta'] else "",
            ])
    with open(Path(output+"_not_assigned").with_suffix(".csv"), mode='w', encoding='utf-8-sig', newline='') as csvfile:
        projects_writer = csv.writer(csvfile)
        projects_writer.writerow([
            'path',
            'name',
            'professor',
            'title',
            'continuation',
            'confidential',
            'departments',
            'orientations',
            'languages',
            'max_students',
            'professors',
            'assistants',
            'assigned_to',
            'weight',
        ])

        
        for p in project_list:
            if(len(clean_list(p['meta'].get('assigned_to', [])))==0):
                projects_writer.writerow([
                    p['path'],
                    p['name'],
                    p['author'],
                    p['meta']['title'],
                    p['meta']['continuation'],
                    p['meta']['confidential'],
                    ", ".join(clean_list(p['meta'].get('departments', []))),
                    ", ".join(clean_list(p['meta'].get('orientations', []))),
                    ", ".join(clean_list(p['meta'].get('languages', []))),
                    p['meta']['max_students'],
                    ", ".join(clean_list(p['meta'].get('professors', []))),
                    ", ".join(clean_list(p['meta'].get('assistants', []))),
                    "",
                    p['meta']['weight'] if "weight" in p['meta'] else "",
                ])
    if update_assignations:
        url = hashlib.md5((project_type+academic_year+secret+"updated").encode()).hexdigest()[:10]
    else:
        url = hashlib.md5((project_type+academic_year+secret).encode()).hexdigest()[:10]
    os.system("hugo -s web -d ../public/"+url)
    logging.info("URL: "+url)
    shutil.copy(base_dir/"resources/robots.txt", "public/robots.txt")

if __name__ == "__main__":
    cli()
