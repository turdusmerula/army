from army.api.log import log
from army.api.debugtools import print_stack
from army.api.package import Package
import toml.decoder
import os
import subprocess
import tempfile
import shutil
import zipfile

# from army.api.config import ArmyConfigFile, Config, ConfigString, ConfigVersion
# from army.api.config import ConfigList, ConfigStringList, ConfigDict

# load project army file 
# @param parent parent configuration
# @param prefix mainly used for unit tests purpose
# @return the loaded project configuration or None if project was not loaded
def load_project(path='army.toml'):
    
    # TODO find a way to add line to error message
    file = os.path.expanduser(path)
    if os.path.exists(file)==False:
        raise ProjectException(f"{file}: file not found")

    content = {}
    try:
        log.info(f"Load project '{file}'")
        content = toml.load(file)
        log.debug(f"content: {content}")
    except toml.decoder.TomlDecodeError as e:
        print_stack()
        log.debug(e)        
        raise e
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ProjectException(f"{format(e)}")
    
    project = Project(data=content)
    project.check()
        

    return project

class ProjectException(Exception):
    def __init__(self, message):
        self.message = message


class Project(Package):
    def __init__(self, data):
        super(Project, self).__init__(data, schema={})

    def package(self, path, output_path):

        # execute prebuild step
        if os.path.exists(os.path.expanduser(os.path.join(path, 'pkg', 'prebuild'))):
            log.info("execute prebuild script")
            subprocess.check_call([os.path.join(os.path.expanduser(path), 'pkg', 'prebuild')])

        # create temporary folder
        d = tempfile.TemporaryDirectory()
        
        files = []
        for include in self.packaging.include:
            files.append(include)
        files.append('army.toml')
        
        # copy files
        for include in files:
            source = os.path.join(os.path.expanduser(path), include)
            dest = d.name
            
            if os.path.exists(source)==False:
                raise ProjectException(f"{include}: package item does not exists")
            
            try:
                if os.path.isfile(source):
                    shutil.copy(source, dest)
                else:
                    shutil.copytree(source, os.path.join(dest, os.path.basename(source)), dirs_exist_ok=True)
            except Exception as e:
                print_stack()
                log.debug(e)
                raise ProjectException(f"{e}")
        
        # TODO add exclude
        # create zip file
        pkg_name = f"{self.name}-{self.version}.zip"
        pkg_path = os.path.join(os.path.expanduser(path), output_path, pkg_name)
        if os.path.exists(pkg_path):
            log.info(f"remove existing file {pkg_path}")
            os.remove(pkg_path)
        if os.path.exists(output_path)==False:
            os.mkdir(output_path)

        log.info(f"create file {pkg_path}")        
        with zipfile.ZipFile(pkg_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(d.name):
                for file in files:
                    zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), d.name))
        
        
        # execute postbuild step
        if os.path.exists(os.path.expanduser(os.path.join(path, 'pkg', 'postbuild'))):
            log.info("execute postbuild script")
            subprocess.check_call([os.path.join(os.path.expanduser(path), 'pkg', 'postbuild')])

        return pkg_path
