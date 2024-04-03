import dedalus.public as d3
import numpy as np

from typing import Tuple
import tqdm
from perlin_noise import PerlinNoise

from src.utils.animation import animate_simulation

def solve_equation(timestepper = d3.SBDF4,
                   step_size: float = 1e-2,
                   save_dt: float = 8,
                   domain_bounds: Tuple[int] = (128,128),
                   grid_size: Tuple[int] = (128, 128),
                   t_max: float = 1024,
                   num_workers: int = 1):
    

    # Parameters
    Nx, Ny = grid_size
    Dx, Dy = domain_bounds

    dealias = 3/2
    dtype = np.float64

    # Bases
    coords = d3.CartesianCoordinates('x', 'y')
    dist = d3.Distributor(coords, dtype=dtype)
    xbasis = d3.RealFourier(coords['x'], size=Nx, bounds=(0, Dx), dealias=dealias)
    ybasis = d3.RealFourier(coords['y'], size=Ny, bounds=(0, Dy), dealias=dealias)


    # Fields
    u = dist.Field(name='u', bases=(xbasis, ybasis))

    # Substitutions
    dx = lambda A: d3.Differentiate(A, coords['x'])
    dy = lambda A: d3.Differentiate(A, coords['y'])
    D = 1e-0
    gamma = 0.5

    # Problem
    problem = d3.IVP([u], namespace=locals())

    # Add main equation, with linear terms on the LHS and nonlinear terms on the RHS
    dedalus_eq_str = "dt(u) + D*lap(u) + D*gamma*lap(lap(u)) = D*lap(u**3)"
    problem.add_equation(dedalus_eq_str)


    # Build solver
    solver = problem.build_solver(timestepper)
    solver.stop_sim_time = t_max

    u['g'] = np.random.uniform(-1,1,grid_size)

    # Setup storage
    u.change_scales(1)
    u_list = [np.copy(u['g'])]
    t_list = [solver.sim_time]


    # Main loop
    bar_format = "{l_bar}{bar}| {n:.02f}/{total:.02f}"
    prog_bar = tqdm.tqdm(total=t_max, bar_format=bar_format)
    next_save_at = save_dt
    while solver.proceed:
        solver.step(step_size)
        prog_bar.update(step_size)
        if solver.sim_time > next_save_at:
            u.change_scales(1)
            u_list.append(np.copy(u['g']))
            t_list.append(solver.sim_time)
            next_save_at += save_dt

    # Convert storage lists to arrays
    u_array = np.array(u_list)
    t_array = np.array(t_list)

    return u_array, t_array


if __name__ == "__main__":
    u, t = solve_equation()
    
    animate_simulation(u)