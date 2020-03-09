#!/bin/python3
import shutil
import os
import extargparse
import pkg_resources
import sys
from pathlib import Path
from template import ArmyTemplate
from git import Repo
from email.policy import default
from config import Config

def init_parser(parentparser, config):
#     parser = group.add_parser('build', help='Build commands')
    parser = parentparser.add_parser('compile', help='Compile project')
    parser.add_argument('--debug', action='store_true', help='Build with debug options')
    parser.add_argument('-j', '--jobs',  type=int, default=1, help='Number of parallel builds (default 1)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Perform verbose build')
    parser.set_defaults(func=project_build)

def clean_exit():
#     # clean elf files to avoid uploading a wrong one
#     find ${PROJECT_PATH}/output -name "*.elf" -exec rm -f {} \; 2>/dev/null
#     
#     echo "Build failed" >&2
#     exit 1
    pass

def project_build(args, config, **kwargs):
    build_debug = args.debug
    build_verbose = args.verbose
    build_jobs = args.jobs
    
    # TODO check if project contains a configuration file
    
    print("[COMPILE]")
    
    cmake_opts = ""
    make_opts = ""
    
    if build_debug:
        cmake_opts = f"{cmake_opts} -DCMAKE_BUILD_TYPE=Debug"
    else:
        cmake_opts = f"{cmake_opts} -DCMAKE_BUILD_TYPE=Release"

    if build_verbose:
        cmake_opts = f"{cmake_opts} -DCMAKE_VERBOSE_MAKEFILE=ON"
    else:
        cmake_opts = f"{cmake_opts} -DCMAKE_VERBOSE_MAKEFILE=OFF"

    if build_jobs:
        make_opts = f"{make_opts} -j{build_jobs}"
 
    # TODO force rebuild elf file even if not changed
    # find ${PROJECT_PATH}/output -name "*.elf" -exec rm -f {} \; 2>/dev/null

    build_path = config.output_path
# export toolchain_path=${BOARD_PATH}/toolchain
# CMAKE_TOOLCHAIN_FILE=${toolchain_path}/cmake/toolchain.cmake
    try:
        # generate cmake file
# mkdir -p ${build_path} || clean_exit
# cmake -B${build_path} -H. -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE} $cmake_opts || clean_exit
        pass
    except:
        clean_exit()
    
    try: 
        # build now
# cd ${build_path}
# make $make_opts || clean_exit
# cd -  
        pass    
    except:
        clean_exit()

# # execute commands left
# if [[ ${#getopt_args[@]} -ne 0 ]]
# then
#     ${xpl_path}/../../build "${getopt_args[@]}"
# fi
