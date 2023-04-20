import sys
import os
sys.path.append(os.getcwd())

from src.utils.animation import animate_multiple_simulations, animate_simulation
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

X1 = read_simulation_from_tar("data/batch_1_grid_128_degree_1_order_2_coef_10.0_terms_5.tar", 1)
animate_simulation(X1)