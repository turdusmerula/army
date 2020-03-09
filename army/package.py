import toml
import os
import sys
import shutil
import glob
import tempfile
import zipfile

class PackageException(Exception):
    def __init__(self, message):
        self.message = message

class Package():
    def __init__(self):
        self.files = {}
        
        self.packaging_path = None
        
    def create_package(self, basedir, name):
        self.packaging_basedir = basedir
        self.packaging_path  =  tempfile.TemporaryDirectory()
        self.package_name = name
        
        print(f"{self.packaging_path.name}")
        
    def add_files(self, path):
        files = glob.glob(path)
        if len(files)==0:
            raise PackageException(f"file not found '{path}'")
        for file in files:
            if os.path.exists(os.path.join(self.packaging_basedir, file))==False:
                raise PackageException(f"file not found '{file}'")
            print(f"- {file}")
            if os.path.dirname(file)=='':
                if os.path.isfile(file):
                    shutil.copy(file, self.packaging_path.name)
                else:
                    shutil.copytree(file, os.path.join(self.packaging_path.name, file))                    
            else:
                dest = os.path.join(self.packaging_path.name, os.path.dirname(file))
                os.makedirs(dest)
                shutil.copytree(file, os.path.join(dest, os.path.basename(file)))

    def package(self):
        print(f"create zip file {self.package_name}")
        zip = zipfile.ZipFile(self.package_name, 'w', zipfile.ZIP_DEFLATED)

        cwd = os.getcwd()
        os.chdir(self.packaging_path.name)
        for root, dirs, files in os.walk('.'):
            for file in files:
                zip.write(os.path.join(root, file))
        zip.close()
        os.chdir(cwd)