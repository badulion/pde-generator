import sys
import os
sys.path.append(os.getcwd())

from src.utils.animation import animate_multiple_simulations
import io
import numpy as np
import tarfile
import fnmatch

def read_simulation_from_tar(tarfile_path: str, sim_num: int = 0):
    with tarfile.open(tarfile_path) as f:
        data_list = fnmatch.filter(f.getnames(), "*.data")
        bytes = f.extractfile(data_list[sim_num]).read()
        bytes_io = io.BytesIO(bytes)
        X = np.load(bytes_io)
        return X

X1 = read_simulation_from_tar("data/batch_1_grid_128_degree_2_order_4_coef_10_terms_7.tar", 0)
X2 = read_simulation_from_tar("data/batch_1_grid_128_degree_2_order_4_coef_10_terms_7.tar", 1)
X3 = read_simulation_from_tar("data/batch_1_grid_128_degree_2_order_4_coef_10_terms_7.tar", 2)
X4 = read_simulation_from_tar("data/batch_1_grid_128_degree_2_order_4_coef_10_terms_7.tar", 3)
animate_multiple_simulations([X1, X2, X3, X4])