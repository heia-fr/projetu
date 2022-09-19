from email.policy import default
import logging
import click
import gitlab

def add_tag_recursive(gitlab_instance, group_id, tag, override_tag=False):
    group = gitlab_instance.groups.get(group_id)
    subgroups = group.subgroups.list(all=True)
    for sg in subgroups:
        add_tag_recursive(gitlab_instance,sg.id,tag,override_tag)
    projects = group.projects.list(all=True)
    project: gitlab.base.RESTObject
    for gp in projects:
        add_tag_project(gitlab_instance, gp.id, tag, override_tag)


def add_tag_project(gitlab_instance, project_id, tag, override_tag=False):
    project = gitlab_instance.projects.get(project_id)
    if tag in [t.name for t in project.tags.list()]:
        if override_tag:
            logging.info(f"Project '{project.name}' already have a tag '{tag}' and will be override")
            try:
                project.tags.delete(id=tag)
                project.tags.create({'tag_name': tag, 'ref': project.default_branch})
                logging.info(f"Project '{project.name}' tag '{tag}' overrided")
            except Exception as e:
                print("Erreur")
                logging.error(e)
        else:
            logging.info(f"Project '{project.name}' already have a tag '{tag}', ignore it")
    else:
        try:
            project.tags.create({'tag_name': tag, 'ref': project.default_branch})
            logging.info(f"Project '{project.name}' is now tag with '{tag}'")
        except Exception as e:
            logging.error(e)


@click.command()
@click.option('--gitlab', 'gitlab_host', type=str, default="https://gitlab.forge.hefr.ch/")
@click.option('--token', type=str, required=True)
@click.option('--group', 'group_path', type=str, default="travaux-etudiants-isc")
@click.option('--tag', type=str, required=True)
@click.option('--override', type=bool, default=False)
@click.option('--debug/--no-debug')
@click.option('--project', type=int, default=None)
def cli(gitlab_host, token, group_path, tag, override, debug, project):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    if tag.lower()=="none":
        logging.error("A tag must be provided to tag projects")
    gl = gitlab.Gitlab(gitlab_host, private_token=token)

    if project is not None:
        add_tag_project(gl, project, tag, override)
        exit()

    # get group id for group path in params
    group_id = -1
    for group in gl.groups.list(search=group_path):
        if group.path == group_path or group.full_path == group_path:
            group_id = group.id
            break
        elif group.full_path.startswith(group_path) and group.full_path.count('/')==1:
            group_id = group.parent_id
            break
    if group_id==-1:
        logging.error(f"Group '{group_path}' not found")
        return
    add_tag_recursive(gl, group_id, tag, override)
    
    

if __name__ == "__main__":
    cli()