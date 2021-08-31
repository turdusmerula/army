from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile_list, load_profile, load_current_profile_cache
from army.api.project import load_project
import sys
import yaml

@parser
@group(name="project")
@command(name="project")
@command(name='inspect', help='Inspect project')
@argument(name="project", help="[PATH]", count='?')
def project_inspect(ctx, project, **kwargs):
    log.info(f"project inspect {project}")

    if project==[]:
        # load project
        project = ctx.project
        if project is None:
            print(f"no project loaded", file=sys.stderr)
            exit(1)
    else:
        try:
            project = load_project(path=project, exist_ok=False)
        except Exception as e:
            print_stack()
            log.fatal(f"{e}")        
            print(f"Error loading project", file=sys.stderr)
            exit(1)
    
    print(yaml.dump(project._data))
    
