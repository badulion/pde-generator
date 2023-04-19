import sys
import os
sys.path.append(os.getcwd())

import numpy as np
import matplotlib.pyplot as plt
from src.utils.animation import animate_solution

from src.equations.generator import EqGenerator
from src.equations.initial import rbf_init
from findiff import FinDiff

from scipy.integrate import solve_ivp

gen = EqGenerator(max_order=3)
eq = gen.random_polynomial()

init = rbf_init((128, 128), padding=4)


d2_dx2 = FinDiff(0, 1, 2)

def derivative(t, y):
    y = y.reshape((128, 128))
    dy = d2_dx2(y)
    return dy.flatten()

sol = solve_ivp(derivative, (0, 5000), y0=init.flatten(), t_eval=np.arange(0, 5000, 50), method="DOP853")

sol = sol.y.reshape((128,128,-1))
sol = np.transpose(sol, (2, 0, 1))
animate_solution(sol)