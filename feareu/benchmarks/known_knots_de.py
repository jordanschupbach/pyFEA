import numpy as np
import splipy
import matplotlib.pyplot as plt
import math
from feareu.experiments.general_fea_experiments.slow_bspline_eval import SlowBsplineEval
from feareu.base_algos.bspline_specific.known_knot_bspline_fea_de import KnownKnotBsplineFeaDE
from feareu.experiments.general_fea_experiments.automated_factors import linear_factorizer

# random.seed(42)
# np.random.seed(42)

class KnownKnotsDe():
    def __init__(self, number_of_knots, number_of_points, max_error, delta, overlap, factor_size, diagnostics_amount, pop_size, mutation_factor = 0.5, crossover_rate = 0.9):
        self.number_of_knots = number_of_knots
        self.number_of_points = number_of_points
        self.max_error = max_error
        self.delta = delta
        self.diagnostics_amount = diagnostics_amount
        self.pop_size = pop_size
        self.mutation_factor = crossover_rate
        self.crossover_rate = mutation_factor
        self.factor_size = factor_size
        self.overlap = overlap
    def run(self):
        thetas = np.random.normal(0.0, 1.0, self.number_of_knots+3) # coefficients for the curve
        interior_knots = np.sort(np.random.uniform(0.0, 1.0, self.number_of_knots)) # knot locations
        knots = np.concatenate(([0.0, 0.0, 0.0],  interior_knots,  [1.0, 1.0, 1.0]))
        bspline_basis = splipy.BSplineBasis(3, knots, -1) # bspline basis
        x = np.random.uniform(0.0, 1.0, self.number_of_points) # x locations for data
        xseq = np.linspace(0.01, 0.99, 1000)
        xmat = bspline_basis(x)
        xseq_mat = bspline_basis(xseq)
        epsilon = np.random.normal(0.0, 0.1, self.number_of_points)
        true_y = xmat @ thetas
        y = true_y + epsilon
        true_yseq = xseq_mat @ thetas
        """plt.scatter(x, y)
        plt.ylim(-2.0, 2.0)
        plt.plot(xseq, true_yseq, color = 'red')
        plt.plot(knots, [-2] * (self.number_of_knots+6), '|', markersize=20)
        plt.show()"""
        # MSE at this solution.
        scatter_plot = SlowBsplineEval(x, y)
        print(scatter_plot(knots))
        fct = linear_factorizer(self.factor_size, self.overlap, self.number_of_knots)
        fact_dom = np.zeros((self.number_of_knots,2))
        fact_dom[:,0] = 0
        fact_dom[:,1] = 1
        testing = KnownKnotBsplineFeaDE(function = scatter_plot, early_stop=500, true_error=scatter_plot(knots), delta = self.delta, og_knot_points = interior_knots, domain=fact_dom, pop_size=self.pop_size, mutation_factor = self.mutation_factor, crossover_rate = self.crossover_rate)
        testing.run()
        testing.diagnostic_plots()
        plt.show()