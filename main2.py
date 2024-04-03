import os
# set environment variables
#os.environ["OMP_NUM_THREADS"] = "1"
#os.environ["NUMEXPR_NUM_THREADS"] = f"16"
#os.environ["NUMEXPR_MAX_THREADS"] = f"16"

import numpy as np
import warnings
import argparse


from src.equations.generator import EqGenerator
from src.utils.archive import write_np_array_to_tar, write_str_to_tar, read_seeds_from_tar
from src.solvers.dedalus import solve_equation
from src.equations.initial import rbf_init


def solve_equation_from_str(args):
    initial_condition = rbf_init((args.grid_size, args.grid_size), seed=args.seed)
    try:
        # run solver
        equation_as_poly = EqGenerator.parse_equation_from_string(args.equation)
        data, times, points = solve_equation(equation_as_poly, 
                                             initial_condition, 
                                             domain_bounds=(args.domain_bounds,args.domain_bounds),
                                             t_max=args.t_max,
                                             step_size=args.step_size,
                                             save_dt=args.save_dt)
        # save equation
        if not os.path.exists(args.save_dir):
            os.makedirs(args.save_dir, exist_ok=True)
        with open(os.path.join(args.save_dir, args.save_name+"_equation.txt"), 'w') as f:
            f.write(args.equation)
        np.savez_compressed(os.path.join(args.save_dir, args.save_name+"_data.npy"), data)
        np.save(os.path.join(args.save_dir, args.save_name+"_data.npy"), data)
        np.save(os.path.join(args.save_dir, args.save_name+"_points.npy"), points)
        np.save(os.path.join(args.save_dir, args.save_name+"_times.npy"), times)
    except RuntimeError:
        warnings.warn(f"Seed {args.seed} produces an unsolvable system. Skipping.", RuntimeWarning)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dataset generator.')

    parser.add_argument('--equation', '-e', type=str, default="1.0*u_x_1_y_0^1+1.0*u_x_0_y_1^1")
    parser.add_argument('--save-dir', '-p', type=str, default="data/")
    parser.add_argument('--save-name', '-n', type=str, default="example")
    parser.add_argument('--seed', '-s', type=int, default=42)
    parser.set_defaults(run_generator=solve_equation_from_str)


    parser.add_argument('--grid-size', '-g', type=int, default=128, help='Size of the grid')
    parser.add_argument('--domain-bounds', '-db', type=int, default=32, help='Size of the domain')
    parser.add_argument('--step-size', '-st', type=float, default=0.01, help='Step size of the solver')
    parser.add_argument('--save-dt', '-dt', type=float, default=1, help='How often to save the state')
    parser.add_argument('--t_max', '-m', type=float, default=128, help='How often to save the state')

    args = parser.parse_args()

    args.run_generator(args)
