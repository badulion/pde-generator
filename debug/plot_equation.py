import sys
import os
sys.path.append(os.getcwd())

from src.utils.animation import animate_multiple_simulations, animate_simulation
import io
import numpy as np
import tarfile
import fnmatch

def read_simulation_from_tar_by_id(tarfile_path: str, sim_num: int = 0):
    with tarfile.open(tarfile_path) as f:
        data_list = fnmatch.filter(f.getnames(), "*.data")
        bytes = f.extractfile(data_list[sim_num]).read()
        bytes_io = io.BytesIO(bytes)
        X = np.load(bytes_io)
        return X

def read_simulation_from_tar_by_name(tarfile_path: str, seed_num: int = 0):
    with tarfile.open(tarfile_path) as f:
        bytes = f.extractfile(f"{seed_num}.data").read()
        bytes_io = io.BytesIO(bytes)
        X = np.load(bytes_io)
        return X
X1 = read_simulation_from_tar_by_name("data/batch_2_grid_128_degree_2_order_2_coef_1_terms_7.tar", 190013844)
X1 = np.load("data/example_data.npy")
animate_simulation(X1)