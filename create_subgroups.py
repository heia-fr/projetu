import logging
import click
import gitlab

def create_subgroup(username,group_id,gitlab_instance):
    # check if username if correct
    users = gitlab_instance.users.list(username=username)
    if len(users)!=1:
        loggin.error(f"Username '{username}' not found in gitlab")
        return
    user = users[0]
    subgroup_url = username.replace('.','_')
    # check if group already exist
    subgroups = gitlab_instance.groups.list(search="travaux-etudiants-isc/"+subgroup_url)
    if len(subgroups)!=0:
        logging.info(f"Subgroup '{subgroup_url}' already exist")
    else:
        subgroup = gitlab_instance.groups.create({'name': user.name, 'path': subgroup_url, 'parent_id': 3063, 'visibility': 'private'})
        subgroup.members.create({'user_id': user.id, 'access_level': gitlab.const.MAINTAINER_ACCESS})
        logging.info(f"Subgroup '{subgroup_url}' for user '{username}' created")

@click.command()
@click.option('--gitlab', 'gitlab_host', type=str, default="https://gitlab.forge.hefr.ch/")
@click.option('--token', type=str, required=True)
@click.option('--group', 'group_path', type=str, default="travaux-etudiants-isc")
@click.option('--profs', 'profs_file', type=click.File('r'), required=True)
@click.option('--debug/--no-debug')
def cli(gitlab_host, token, group_path, profs_file, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    gl = gitlab.Gitlab(gitlab_host, private_token=token)
    profs = [line.strip() for line in profs_file]

    # get group id for group path in params
    group_id = -1
    for group in gl.groups.list(search=group_path):
        if group.path==group_path:
            group_id = group.id
    if group_id==-1:
        logging.error(f"Group '{group_path}' not found")
        return
    # create non existant subgroups
    for prof in profs:
        create_subgroup(prof,group_id,gl)
    
    # check if there is subgroups non matching with profs
    subgroups = gl.groups.get(group_id).subgroups.list()
    for subgroup in subgroups:
        if subgroup.path.replace('_','.') not in profs:
            logging.warning(f"Found a subgroup '{subgroup.path}' but no prof with this username")
    

if __name__ == "__main__":
    cli()