import numpy as np
from typing import List
import re


class EqGenerator():
    def __init__(self, variables: List[str] = ['x', 'y'], max_order: int = 3) -> None:
        

        self.derivatives = [c for c in EqGenerator.partial_derivatives(variables, max_order)]
        self.variables = variables
        self.max_order = max_order


    def compositions(n, k):
        if n < 0 or k < 0: 
            return
        elif k == 0:
            if n == 0:
                yield []
            return
        elif k == 1:
            yield [n]
            return 
        else:
            for i in range(0,n+1):
                for comp in EqGenerator.compositions(n-i, k-1):
                    yield [i] + comp

    def partial_derivatives(variables, max_order):
        k = len(variables)
        for n in range(0,max_order+1):
            for c in EqGenerator.compositions(n, k):
                yield 'u' + ''.join([f'_{variables[i]}_{c[i]}' for i in range(k)])

    def polynomial_terms(terms, max_degree):
        k = len(terms)
        for n in range(1,max_degree+1):
            for c in EqGenerator.compositions(n, k):
                yield [(terms[i], c[i])  for i in range(k) if c[i] != 0]

    def random_polynomial(self, max_degree:int = 3, num_terms: int = 5, seed: int = 42, max_coef: float = 1):
        np.random.seed(seed)

        poly_terms = [c for c in EqGenerator.polynomial_terms(self.derivatives, max_degree)]

        num_all_terms = len(poly_terms)
        num_selected_terms = num_terms

        selected_terms_indices = np.random.choice(num_all_terms, num_selected_terms, replace=False)
        selected_terms = [poly_terms[i] for i in selected_terms_indices]
        coefficients = np.random.uniform(-max_coef, max_coef, num_selected_terms)
        coefficients = np.round(coefficients, 3)
        expression = [[coef] + term for coef, term in zip(coefficients, selected_terms)]
        return expression
    
    def convert_equation_to_string(expression):
        def generate_term_str(term):
            coef = term[0]
            term = term[1:]
            components = [f"{coef}"] + [f"{variable[0]}^{variable[1]}" for variable in term]
            return "*".join(components)
        monomials_with_coefficient = [generate_term_str(term) for term in expression]
        return '+'.join(monomials_with_coefficient)
    
    def parse_equation_from_string(expression: str):
        terms = re.split("[+]", expression)
        def parse_term(term):
            parts = re.split("[*|^]", term)
            eq = [float(parts[0])]+[(parts[i], int(parts[i+1])) for i in range(1, len(parts), 2)]
            return eq
        return [parse_term(t) for t in terms]

    def convert_equation_to_lines(expression):
        def generate_term_line(term):
            coef = term[0]
            term = term[1:]
            components = [f"{coef}"] + [f"{variable[0]} {variable[1]}" for variable in term]
            return " ".join(components)
        poly_as_lines = [generate_term_line(term) for term in expression]
        return poly_as_lines
    
    def tokenize_equation(expression):
        def decimal_separator_check(char: str):
            if char == ".":
                return "<DECIMAL>"
            return char

        def tokenize_term(term):
            sequence = [] if term[0] >= 0 else ['<NEG>']
            sequence += [decimal_separator_check(s) for s in str(abs(term[0]))]
            for i in range(1,len(term)):
                sequence += [f"<{term[i][0]}>", "<POW>", f"{term[i][1]}"]
                if i+1 < len(term):
                    sequence += ['<MUL>']
            return sequence
        
        tokens = []
        for term in expression:
            tokens += tokenize_term(term)
        return ['<SOS>'] + tokens + ['<EOS>']


    def parse_equation_from_lines(file):
        def parse_line(line):
            parts = line.split(" ")
            eq = [float(parts[0])]+[(parts[i], int(parts[i+1])) for i in range(1, len(parts), 2)]
            return eq
        with open(file,'r') as f:
            lines = f.read().splitlines()
        return [parse_line(l) for l in lines]