from pde import (
    ScalarField, 
    FieldCollection, 
    PDEBase, 
    FieldBase, 
    UnitGrid, 
    CallbackTracker,
    ProgressTracker
)

from pde.trackers.base import TrackerCollection

import matplotlib.pyplot as plt
import numpy as np


from initial import rbf_init


class PolynomialPDE(PDEBase):
    def __init__(self, equation, bc = 'auto_periodic_neumann') -> None:
        super().__init__()

        self.equation = equation
        self.bc = bc

    def get_partial_derivative(self, u, derivative_str):
        bc = 'auto_periodic_neumann'
        derivative_components = derivative_str.split('_')
        order_x = int(derivative_components[2])
        order_y = int(derivative_components[4])
        for i in range(order_x):
            u = u.gradient(bc)[0]
        for i in range(order_y):
            u = u.gradient(bc)[1]
        return u
    
    def extract_coordinates_from_grid(self, grid):
        shape = grid.shape
        x_bounds = grid.axes_bounds[0]
        y_bounds = grid.axes_bounds[1]
        x = (grid.cell_coords[:,:,0]-x_bounds[0])/(x_bounds[1]-x_bounds[0])
        y = (grid.cell_coords[:,:,1]-y_bounds[0])/(y_bounds[1]-y_bounds[0])
        return x, y



    def get_term(self, u, term):
        result = term[0]
        for t in term[1:]:
            result *= self.get_partial_derivative(u, t[0])**t[1]
        return result
    
    def get_initial_state(self, grid, seed=42):
        """prepare a useful initial state"""

        # initialize fields
        u = ScalarField(grid, rbf_init(grid.shape, seed=seed), label="u")
        #u = ScalarField(grid, self.rbf_init(x, y, period=10), label="u")
        return u
    
    def evolution_rate(self, state: FieldBase, t: float = 0) -> FieldBase:
        terms = [self.get_term(state, term) for term in self.equation]
        derivative = sum(terms)

        return sum(terms)