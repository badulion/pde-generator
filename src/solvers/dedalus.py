

from typing import Tuple, List, Any

import numpy as np
import dedalus.public as d3
import logging
import tqdm

logger = logging.getLogger(__name__)

def get_derivative_as_dedalus_symbol(derivative_str: str):
    # decode the derivative str
    derivative_codes = derivative_str.split("_")
    variable_1 = derivative_codes[1]
    order_variable_1 = int(derivative_codes[2])
    variable_2 = derivative_codes[3]
    order_variable_2 = int(derivative_codes[4])


    dedalus_symbol = f"d{variable_1}("*order_variable_1 + \
                     f"d{variable_2}("*order_variable_2 + \
                      "u"+")"*(order_variable_1+order_variable_2)
    return dedalus_symbol


def dedalus_eq_str_from_poly(eq_poly: List[Any]):
    def str_from_one_derivative(der: Tuple):
        if der[1] == 1:
            return f"{get_derivative_as_dedalus_symbol(der[0])}"
        else:
            return f"{get_derivative_as_dedalus_symbol(der[0])}**{der[1]}"
        
    def str_from_one_term(term: List, sign: int = 1):
        derivatives = [str_from_one_derivative(der) for der in term[1:]]
        coefficient = f"{'+' if np.sign(sign)*term[0] > 0 else ''}{np.sign(sign)*term[0]}"
        components = [coefficient] + derivatives
        return "*".join(components)
        
    linear_terms = filter(lambda term: len(term) == 2 and term[1][1] == 1, eq_poly)
    nonlinear_terms = filter(lambda term: len(term) > 2, eq_poly)
    #return str_from_one_term(next(nonlinear_terms))

    linear_terms_str = [str_from_one_term(term, sign=-1) for term in linear_terms]
    nonlinear_terms_str = [str_from_one_term(term, sign=1) for term in nonlinear_terms]
    LHS = "dt(u)"+"".join(linear_terms_str)

    RHS = "0"+"".join(nonlinear_terms_str)
    return LHS+"="+RHS


def solve_equation(eq_poly: List, 
                   initial_condition: np.ndarray,
                   timestepper: d3.MultistepIMEX = d3.SBDF4,
                   step_size: float = 1e-2,
                   save_dt: float = 0.1,
                   domain_bounds: Tuple[int] = (1,1),
                   t_max: float = 128,
                   num_workers: int = 1):
    

    # Parameters
    Nx, Ny = initial_condition.shape
    Dx, Dy = domain_bounds

    dealias = 3/2
    dtype = np.float64

    # Bases
    coords = d3.CartesianCoordinates('x', 'y')
    dist = d3.Distributor(coords, dtype=dtype)
    xbasis = d3.RealFourier(coords['x'], size=Nx, bounds=(0, Dx), dealias=dealias)
    ybasis = d3.RealFourier(coords['y'], size=Ny, bounds=(0, Dy), dealias=dealias)

    xgrid, ygrid = np.meshgrid(xbasis.global_grid(scale=1).ravel(), ybasis.global_grid(scale=1).ravel())
    points = np.stack([xgrid, ygrid])


    # Fields
    u = dist.Field(name='u', bases=(xbasis, ybasis))

    # Substitutions
    dx = lambda A: d3.Differentiate(A, coords['x'])
    dy = lambda A: d3.Differentiate(A, coords['y'])

    # Problem
    problem = d3.IVP([u], namespace=locals())

    # Add main equation, with linear terms on the LHS and nonlinear terms on the RHS
    dedalus_eq_str = dedalus_eq_str_from_poly(eq_poly)
    problem.add_equation(dedalus_eq_str)


    # Build solver
    solver = problem.build_solver(timestepper)
    solver.stop_sim_time = t_max

    u['g'] = initial_condition

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
        if np.isnan(u['g']).any():
            raise RuntimeError("Equation is not well-posed, stopping!")
        elif np.max(np.abs(u['g'])) > 1e+3:
            raise RuntimeError("Equation is not well-posed, stopping!")
        if solver.sim_time > next_save_at:
            u.change_scales(1)
            u_list.append(np.copy(u['g']))
            t_list.append(solver.sim_time)
            next_save_at += save_dt

    # Convert storage lists to arrays
    u_array = np.array(u_list)
    t_array = np.array(t_list)

    return u_array, t_array, points
