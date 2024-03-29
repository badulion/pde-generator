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

def solve_batch_of_random_equations(args):
    gen = EqGenerator(max_order=args.max_equation_order)
    seed_list = read_seeds_from_tar(f"{args.batch}.txt", "config/seeds.tar")
    batch_name = f"batch_{args.batch}_grid_{args.grid_size}_degree_{args.max_equation_degree}_order_{args.max_equation_order}_coef_{args.max_coef}_terms_{args.max_terms}"
    output_tar_path = f"data/{batch_name}.tar"
    N = len(seed_list)
    for i, seed in enumerate(seed_list):
        print(f"Solving equation {i+1} of {N}...")
        np.random.seed(seed)
        num_equation_terms = np.random.choice(range(1,args.max_terms))

        eq = gen.random_polynomial(max_degree=args.max_equation_degree, num_terms=num_equation_terms, seed=seed, max_coef=args.max_coef)
        eq_str = EqGenerator.convert_equation_to_string(eq)
        eq_tokens = EqGenerator.tokenize_equation(eq)
        initial_condition = rbf_init((args.grid_size, args.grid_size), seed=seed)

        try:
            # run solver
            data, times, points = solve_equation(eq, 
                                                 initial_condition, 
                                                 domain_bounds=(args.domain_bounds,args.domain_bounds),
                                                 t_max=args.t_max,
                                                 step_size=args.step_size,
                                                 save_dt=args.save_dt)
            # save equation
            write_str_to_tar('\n'.join(eq_tokens), f"{seed}.tokens", output_tar_path)
            write_str_to_tar(eq_str, f"{seed}.equation", output_tar_path)
            write_np_array_to_tar(data, f"{seed}.data", output_tar_path)
            write_np_array_to_tar(points, f"{seed}.points", output_tar_path)
        except RuntimeError:
            warnings.warn(f"Seed {seed} produces an unsolvable system. Skipping.", RuntimeWarning)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dataset generator.')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_random = subparsers.add_parser('random', help="Generate multiple random equations that are saved into a tar file")
    parser_random.add_argument('--batch', '-b', type=int, default=1, help='batch of equations')
    parser_random.add_argument('--max-equation-degree', '-d', type=int, default=2, help='Max degree of the equation (1 for linear only)')
    parser_random.add_argument('--max-equation-order', '-o', type=int, default=2, help='Max order of the equation')
    parser_random.add_argument('--max-coef', '-c', type=float, default=1, help='Max absolute value of coefficient for each term')
    parser_random.add_argument('--max-terms', '-t', type=int, default=7, help='Max number of different terms in the equation')
    parser_random.set_defaults(run_generator=solve_batch_of_random_equations)


    parser_string = subparsers.add_parser('from_string', help="Generate data for an equations specified by a string.")
    parser_string.add_argument('--equation', '-e', type=str, default="1.0*u_x_1_y_0^1+1.0*u_x_0_y_1^1")
    parser_string.add_argument('--save-dir', '-p', type=str, default="data/")
    parser_string.add_argument('--save-name', '-n', type=str, default="example")
    parser_string.add_argument('--seed', '-s', type=int, default=42)
    parser_string.set_defaults(run_generator=solve_equation_from_str)


    parser.add_argument('--grid-size', '-g', type=int, default=128, help='Size of the grid')
    parser.add_argument('--domain-bounds', '-db', type=int, default=32, help='Size of the domain')
    parser.add_argument('--step-size', '-st', type=float, default=0.01, help='Step size of the solver')
    parser.add_argument('--save-dt', '-dt', type=float, default=1, help='How often to save the state')
    parser.add_argument('--t_max', '-m', type=float, default=128, help='How often to save the state')

    args = parser.parse_args()

    args.run_generator(args)
