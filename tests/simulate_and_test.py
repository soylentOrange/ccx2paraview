#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Solve Calculix examples using pygccx first...
then test ccx2paraview converter on the CalculiX examples' frd-output

Setup of the conda environment is handled by conda wingman extension: 
(You need to open the ccx2paraview_simulate_and_test.yaml in ./tests)
Show and Run Commands > Conda Wingman: Build Conda Environment from YAML file
Show and Run Commands > Conda Wingman: Activate Conda Environment from YAML file

Set the Python Interpreter for VS Code to the environment's one:
Show and Run Commands > Python: Select Interpreter

Ctrl+F5 to run in VSCode. 
"""

# Standard imports
import os
import sys
import time
import shutil
import logging
import subprocess

# add common.py available for import
sys_path = os.path.abspath(__file__)
sys_path = os.path.dirname(sys_path)
sys_path = os.path.join(sys_path, '..')
sys_path = os.path.normpath(sys_path)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

# local imports
# pylint: disable=wrong-import-position
from log import LoggingHandler, print_logfile_line, read_and_log
from ccx2paraview.common import Converter
from ccx2paraview.cli import clean_screen
# pylint: enable=wrong-import-position

file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)
dir_path_logs = os.path.normpath(os.path.join(dir_path, 'test_logs'))
dir_path_frds = os.path.normpath(os.path.join(dir_path, 'sim_frds'))

# Number of cores to use for simulation
N_CORE = int(8)

def clean_cache(folder:str=None):
    """Recursively delete cached files in all subfolders."""
    if folder is None:
        folder = os.getcwd()
    pycache = os.path.join(folder, '__pycache__')
    if os.path.isdir(pycache):
        shutil.rmtree(pycache) # works in Linux as in Windows

    # Recursively clear cache in child folders
    try:
        for f in os.scandir(folder):
            if f.is_dir():
                clean_cache(f.path)
    except PermissionError:
        logging.error('Insufficient permissions for %s', dir)

def clean_results_keep_vtx(folder:str=None):
    """Cleaup old result files keeping the interesting results."""
    if folder is None:
        folder = os.getcwd()
    extensions = ('.dat', '.cvg', '.sta', '.out', '.12d')
    for f in os.scandir(folder):
        if f.is_dir():
            clean_results(f.path)
        if f.name.endswith(extensions):
            try:
                os.remove(f.path)
                sys.__stdout__.write('Deleted ' + f.path + '\n')
            except OSError:
                sys.__stdout__.write(f.path + ': ' + sys.exc_info()[1][1] + '\n')

def clean_results(folder:str=None):
    """Cleaup old result files."""
    if folder is None:
        folder = os.getcwd()
    extensions = ('.vtk', '.vtu', '.vtkhdf', '.pvd', '.dat', '.cvg', '.sta', '.out', '.12d')
    for f in os.scandir(folder):
        if f.is_dir():
            clean_results(f.path)
        if f.name.endswith(extensions):
            try:
                os.remove(f.path)
                sys.__stdout__.write('Deleted ' + f.path + '\n')
            except OSError:
                sys.__stdout__.write(f.path + ': ' + sys.exc_info()[1][1] + '\n')

def get_time_delta(delta):
    """Return spent time delta in format mm:ss.s."""
    return f'{int(delta%3600/60):d}m {delta%3600%60:.1f}s'

def ccx_and_convert_single_file(modelname, inp_path:str=None):
    """solve and convert a single model"""
    ccx_single_file(modelname, inp_path)
    convert_single_file(modelname)

def ccx_single_file(modelname, inp_path:str=None):
    """solve a single model"""

    if inp_path is not None:
        try:
            shutil.copy(\
                os.path.normpath(os.path.join(os.getcwd(), f'{inp_path}', f'{modelname}.inp')), \
                    os.path.normpath(os.path.join(f'{dir_path_frds}', f'{modelname}.inp')))
        # pylint: disable-next=broad-exception-caught
        except Exception as e:
            logging.error(e)

    log_file = os.path.normpath(os.path.join(dir_path_logs, f'{modelname}.ccx.log'))
    try:
        # Prepare logging
        logging_handler_sim = LoggingHandler(log_file)
        logging.getLogger().addHandler(logging_handler_sim)
        logging.getLogger().setLevel(logging.DEBUG)
        print_logfile_line('SIMULATE')
        print_logfile_line('')
        print_logfile_line(f'INFO: Reading {modelname}.inp')
        print_logfile_line(f'INFO: run ccx with {N_CORE} core(s)')
        start = time.perf_counter()

        # run ccx
        env = os.environ
        env['OMP_NUM_THREADS'] = str(N_CORE)
        with subprocess.Popen([shutil.which('ccx'), '-i', modelname],\
                              stdin=subprocess.PIPE,\
                              stdout=subprocess.PIPE,\
                              stderr=subprocess.STDOUT,\
                              cwd=dir_path_frds,\
                              env=env) as sim_process:
            read_and_log(sim_process.stdout)
        delta = time.perf_counter() - start
        print_logfile_line(get_time_delta(delta))
        # end logging
        logging.getLogger().removeHandler(logging_handler_sim)
    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logging.error(e)

def convert_single_file(modelname):
    """test conversion of a single file into all possible formats"""
    frd_file = os.path.normpath(os.path.join(dir_path_frds, f'{modelname}.frd'))
    log_file = os.path.normpath(os.path.join(dir_path_logs, f'{modelname}.convert.log'))
    try:
        # Prepare logging
        logging_handler = LoggingHandler(log_file)
        logging.getLogger().addHandler(logging_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        print_logfile_line('CONVERTER TEST')
        print_logfile_line('')
        start = time.perf_counter()
        ccx2paraview = Converter(frd_file, ['vtk', 'vtu', 'hdf'])
        ccx2paraview.run()
        delta = time.perf_counter() - start
        print_logfile_line(get_time_delta(delta))
        # end logging
        logging.getLogger().removeHandler(logging_handler)
    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logging.error(e)

def convert_single_file_vtu(modelname):
    """test conversion of a single file to vtu"""
    frd_file = os.path.normpath(os.path.join(dir_path_frds, f'{modelname}.frd'))
    log_file = os.path.normpath(os.path.join(dir_path_logs, f'{modelname}.convert.log'))
    try:
        # Prepare logging
        logging_handler = LoggingHandler(log_file)
        logging.getLogger().addHandler(logging_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        print_logfile_line('CONVERTER TEST')
        print_logfile_line('')
        start = time.perf_counter()
        ccx2paraview = Converter(frd_file, ['vtu'])
        ccx2paraview.run()
        delta = time.perf_counter() - start
        print_logfile_line(get_time_delta(delta))
        # end logging
        logging.getLogger().removeHandler(logging_handler)
    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logging.error(e)

def convert_single_file_vtk(modelname):
    """test conversion of a single file to vtk"""
    frd_file = os.path.normpath(os.path.join(dir_path_frds, f'{modelname}.frd'))
    log_file = os.path.normpath(os.path.join(dir_path_logs, f'{modelname}.convert.log'))
    try:
        # Prepare logging
        logging_handler = LoggingHandler(log_file)
        logging.getLogger().addHandler(logging_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        print_logfile_line('CONVERTER TEST')
        print_logfile_line('')
        start = time.perf_counter()
        ccx2paraview = Converter(frd_file, ['vtk'])
        ccx2paraview.run()
        delta = time.perf_counter() - start
        print_logfile_line(get_time_delta(delta))
        # end logging
        logging.getLogger().removeHandler(logging_handler)
    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logging.error(e)

def convert_single_file_hdf(modelname):
    """test conversion of a single file to hdf"""
    frd_file = os.path.normpath(os.path.join(dir_path_frds, f'{modelname}.frd'))
    log_file = os.path.normpath(os.path.join(dir_path_logs, f'{modelname}.convert.log'))
    try:
        # Prepare logging
        logging_handler = LoggingHandler(log_file)
        logging.getLogger().addHandler(logging_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        print_logfile_line('CONVERTER TEST')
        print_logfile_line('')
        start = time.perf_counter()
        ccx2paraview = Converter(frd_file, ['hdf'])
        ccx2paraview.run()
        delta = time.perf_counter() - start
        print_logfile_line(get_time_delta(delta))
        # end logging
        logging.getLogger().removeHandler(logging_handler)
    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        logging.error(e)

def prepare_folders(folders:list=None):
    """Create frd and log folder"""
    for folder in folders:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

# Run
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))

    # create folders for logs and frds if not present
    try:
        prepare_folders([dir_path_logs, dir_path_frds])
    except PermissionError:
        print("Cannot create directories.")
        sys.exit(0)

    clean_cache()
    clean_results(dir_path_logs)
    clean_results(dir_path_frds)
    clean_screen()

    #ccx_and_convert_single_file('ball', '../../examples/other')
    ccx_and_convert_single_file('Ihor_Mirzov_baffle_2D', '../../examples/other')
    ccx_and_convert_single_file('dichtstoff_2_HE8', '../../examples/other')
    ccx_and_convert_single_file('Jan_Lukas_modal_dynamic_staticbeam2', '../../examples/other')
    ccx_and_convert_single_file('Kaffeeheblerei_hinge', '../../examples/other')
    ccx_and_convert_single_file('Jan_Lukas_modal_dynamic_beammodal', '../../examples/other')

    #convert_single_file('dichtstoff_2_HE8')
    #convert_single_file_vtu_hdf('dichtstoff_2_HE8')
    #convert_single_file('ball')
    #convert_single_file_vtu('ball')
    #convert_single_file_vtu_hdf('ball')
    #convert_single_file_vtk_vtu('ball')
    #convert_single_file('ball')

    clean_cache()
    clean_results_keep_vtx(dir_path_frds)
