import time
from multiprocessing import freeze_support

import matplotlib.pyplot as plt
import numba
import numpy as np
import pytest
from numpy import cos, e, exp, pi, sqrt, sum

from pyfea import (FEA, BsplineFEA, Function, ParallelBsplineFEA,
                   ParallelVectorBsplineFEA)
from pyfea.base_algos import FeaDE, FeaGA, FeaPso, ParallelFeaPSO
from pyfea.base_algos.traditional.parallel_fea_de import ParallelFeaDE
from pyfea.base_algos.traditional.parallel_fea_ga import ParallelFeaGA
from pyfea.fea import parallel_vector_bspline_fea
from pyfea.fea.vector_comparison_bspline_fea import VectorComparisonBsplineFEA


@numba.jit
def rastrigin__(solution=None):
    """for i in range(10000):
    sum(solution**2 - 10 * cos(2 * pi * solution) + 10)
    """
    return sum(solution**2 - 10 * cos(2 * pi * solution) + 10)


def linear_factorizer(fact_size, overlap, dim):
    smallest = 0
    largest = fact_size
    factors = []
    while largest <= dim:
        factors.append([x for x in range(smallest, largest)])
        smallest = largest - overlap
        largest += fact_size - overlap
    if smallest < dim:
        factors.append([x for x in range(smallest, dim)])
    return factors


array = np.zeros((10))
array[0] = 1
array[1] = 2
domain = np.zeros((10, 2))
domain[:, 0] = -5
domain[:, 1] = 5

if __name__ == "__main__":
    # freeze_support()
    function = Function(array, rastrigin__, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    # rand_factors = [np.random.choice(range(10), replace=False, size=3) for x in range(10)]
    fct1 = [
        [0],
        [0, 1],
        [0, 1, 2],
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
        [4, 5, 6],
        [5, 6, 7],
        [6, 7, 8],
        [7, 8, 9],
        [8, 9],
        [9],
    ]
    fct2 = [
        [0],
        [0, 1],
        [0, 1, 2],
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
        [4, 5, 6],
        [5, 6, 7],
        [6, 7, 8],
        [7, 8, 9],
        [8, 9, 10],
        [9, 10, 11],
        [10, 11, 12],
        [11, 12, 13],
        [12, 13, 14],
        [13, 14],
        [14],
    ]

    og_knots = [0, 0, 0, 0, 0]

    factor_number = 5
    factors = linear_factorizer(2, 1, factor_number)

    """start = time.time()
    fea1 = ParallelBsplineFEA(factors=factors, function = rastrigin__, iterations = 3, dim = factor_number, base_algo_name=FeaPso, domain=(-5, 5), process_count=2, diagnostics_amount=1, generations= 5, pop_size=20)
    fea1.run()
    end = time.time()
    print("non-parallel time: ", end-start)"""

    """
    start = time.time()
    fea2 = ParallelVectorBsplineFEA(factors=factors, function = rastrigin__, iterations = 3, dim = factor_number, base_algo_name=ParallelFeaPSO, domain=(-5, 5), diagnostics_amount=1, og_knot_points=og_knots, process_count=2, process=2, generations= 5, pop_size=10)
    fea2.run()
    end = time.time()
    print("parallel time PSO: ", end-start)
    
    start = time.time()
    fea3 = ParallelVectorBsplineFEA(factors=factors, function = rastrigin__, iterations = 3, dim = factor_number, base_algo_name=ParallelFeaDE, domain=(-5, 5), diagnostics_amount=1, og_knot_points=og_knots, process_count=2, process=2, generations= 5, pop_size=10)
    fea3.run()
    end = time.time()
    print("parallel time DE: ", end-start)
    """

    start = time.time()
    fea4 = ParallelBsplineFEA(
        factors=factors,
        function=rastrigin__,
        iterations=20,
        dim=factor_number,
        base_algo_name=FeaPso,
        domain=(-5, 5),
        diagnostics_amount=1,
        og_knot_points=og_knots,
        process_count=2,
        generations=5,
        pop_size=10,
    )
    fea4.run()
    end = time.time()
    print("parallel time GA: ", end - start)

    start = time.time()
    fea5 = ParallelVectorBsplineFEA(
        factors=factors,
        function=rastrigin__,
        iterations=20,
        dim=factor_number,
        base_algo_name=FeaPso,
        domain=(-5, 5),
        diagnostics_amount=1,
        og_knot_points=og_knots,
        process_count=2,
        generations=5,
        pop_size=10,
    )
    fea5.run()
    end = time.time()
    print("parallel time GA: ", end - start)

    # daig_plt1 = fea1.diagnostic_plots()
    # daig_plt1 = fea2.diagnostic_plots()
    # daig_plt1 = fea3.diagnostic_plots()
    daig_plt1 = fea4.diagnostic_plots()
    # daig_plt1 = fea5.diagnostic_plots()
    plt.show()

