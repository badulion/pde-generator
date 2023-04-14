from pde import (
    UnitGrid, 
    CallbackTracker,
    ProgressTracker
)

from pde.trackers.base import TrackerCollection

import matplotlib.pyplot as plt
import numpy as np
import warnings
import argparse


from eq_generator import EqGenerator
from eq_wrapper import PolynomialPDE
from utils.archive import write_np_array_to_tar, write_str_to_tar


    


def solve_equation(equation: str, save_interval=0.1, tmax = 1, seed=42):
    eq = EqGenerator.parse_equation_from_string(equation)

    p = PolynomialPDE(eq)

    grid = UnitGrid([64, 64], periodic=True)

    state = p.get_initial_state(grid, seed=seed)


    # setup saving equation states
    data = []
    times = []
    def save_state(state, time):
        data.append(state.copy().data)
        times.append(time)


    tracker_callback = CallbackTracker(save_state, interval=save_interval)
    tracker_progress = ProgressTracker(interval=save_interval)
    tracker = TrackerCollection([tracker_callback, tracker_progress])


    # solve
    sol = p.solve(state, t_range=(0, tmax), tracker=tracker)
    data = np.stack(data)
    times = np.stack(times)

    return data, times


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dataset generator.')
    parser.add_argument('--batch', '-b', type=int, default=2, help='batch of equations')

    args = parser.parse_args()

    gen = EqGenerator(max_order=3)
    seed_list = np.loadtxt(f"config/seeds/seeds_{args.batch}.txt", dtype=int)
    N = len(seed_list)
    for i, seed in enumerate(seed_list[127:]):
        print(f"Solving equation {i+1} of {N}...")
        np.random.seed(seed)
        num_equation_terms = np.random.choice(range(1,8))

        eq = gen.random_polynomial(max_degree=3, num_terms=num_equation_terms, seed=seed)
        eq_str = EqGenerator.convert_equation_to_string(eq)

        eq_tokens = EqGenerator.tokenize_equation(eq)


        try:
            # run solver
            data, times = solve_equation(eq_str, tmax=12.8, save_interval=0.2, seed=seed)
            # save equation
            write_str_to_tar('\n'.join(eq_tokens), f"{seed}.tokens", f"data/batch_{args.batch}.tar")
            write_str_to_tar(eq_str, f"{seed}.equation", f"data/batch_{args.batch}.tar")
            write_np_array_to_tar(data, f"{seed}.data", f"data/batch_{args.batch}.tar")
        except:
            warnings.warn(f"Seed {seed} produces an unsolvable system. Skipping.", RuntimeWarning)



