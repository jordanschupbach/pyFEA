import feareu
import matplotlib.pyplot as plt
import logging
from bayes_opt import BayesianOptimization
import pickle
from pathlib import Path
import numpy as np
import time
import math
from copy import deepcopy
from types import NoneType
import splipy
import scipy.sparse.linalg as splinalg
import scipy.sparse as sparse
from scipy.stats import gaussian_kde

best = float("-inf")
number_recorded = 0
x = []
y = []

results_dir = Path('results')
results_dir.mkdir(parents=True, exist_ok=True)
filename = results_dir / f"logging_best.log"
logger = logging.getLogger(__name__)
logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG)


#set the number of processors and the chunksizes used by parallel base algorithms.
processes=4
chunksize=1

#set the number of processes and threads used by a parallel FEA.
process_count=8
thread_count=16

#set the number of iterations at which we record data to be printed.
diagnostics_amount = 2

#set the bounds for your FEA's Bayesian run. 
#IMPORTANT: Only set the variables you want to use as hyperparameters. Comment out the others.

iterations = 100
generations = 1000
pop_size = 300

pbounds = {
    "generations": (2, 30),
    #"iterations": (2, 70),
    "pop_size": (30, 100),
    "fact_size": (1, 50),
    "overlap": (0, 30),
    # "num_covers":(1,5),
    #"num_clamps": (0, 5),
    "dim": (5, 200),
}

base_bounds = {
        #"generations":(5,200),
        #"pop_size":(30,100),
        "dim":(5,200)
        }

pso_bounds = {
       "phi_p":(0.8,3),
       "phi_g":(0.8,3),
       "omega":(0.00000001,0.99)
        }

ga_bounds = {
       "mutation_rate":(0.01,0.99),
       "mutation_range":(0.1,2),
        }

de_bounds = {
       "mutation_factor":(0.1,1), 
       "crossover_rate":(0.1,1),
        }


#choose your factorizer.
factorizer = feareu.linear_factorizer

#set the kind of FEA you want to use.
fea = feareu.ParallelBsplineFEA

def bayes_input_fea(
                fact_size=None,
                overlap=1,
                num_covers=2,
                num_clamps=0,
                generations=20,
                iterations=iterations,
                pop_size=20,
                mutation_factor=0.5,
                crossover_rate=0.9,
                mutation_rate=0.05,
                mutation_range=0.5,
                phi_p=math.sqrt(2),
                phi_g=math.sqrt(2),
                omega=1/math.sqrt(2),
                dim = 10
                ):
    fact_size = int(fact_size)
    dim = int(dim)
    overlap = int(overlap)
    generations = int(generations)
    pop_size = int(pop_size)
    num_covers = int(num_covers)
    num_clamps=int(num_clamps)
    iterations = int(iterations)

    #code for generating domain on normal FEA.
    #domain = np.zeros((dim,2))
    #domain[:,0] = -5
    #domain[:,1] = 5

    global best
    global number_recorded

    #code for generating domain on Bspline FEA. Comment out if you're working on normal FEA.
    domain = (0,1)
    
    factors = factorizer(fact_size=fact_size, overlap=overlap, dim=dim, num_covers=num_covers)
    if factors is None or fact_size > dim:
        return -999999999
    if num_clamps > 0:
        feareu.clamp_factor_ends(dim, factors, num_clamps)
    objective = fea(
                    factors,
                    fitness,
                    iterations,
                    dim,
                    base_alg,
                    domain,
                    diagnostics_amount=diagnostics_amount,
                    process_count=process_count,
                    thread_count=thread_count,
                    pop_size=pop_size,
                    generations=generations,
                    mutation_factor=mutation_factor,
                    crossover_rate=crossover_rate,
                    mutation_rate=mutation_rate,
                    mutation_range=mutation_range,
                    phi_p=phi_p,
                    phi_g=phi_g,
                    omega=omega,
                    processes=processes,
                    chunksize=chunksize)
    ret = -objective.run()
    if ret > best:
        best = ret
        results_dir = Path('results')
        results_dir.mkdir(parents=True, exist_ok=True)
        filename = results_dir / f"FEA_function_{number_recorded}.png"
        plt.figure()
        objective.diagnostic_plots()
        plt.savefig(filename)
        logger.info(f'NEW BEST - NUMBER {number_recorded} ------------------------------------------------')
        logger.info(f'fitness evaluation: {ret}')
        logger.info(f'fact_size: {fact_size}')
        logger.info(f'overlap: {overlap}')
        logger.info(f'num_clamps: {num_clamps}')
        logger.info(f'dim: {dim}')
        logger.info(f'iterations: {iterations}')
        logger.info(f'base_alg: {base_alg.__name__}')
        logger.info(f'pop_size: {pop_size}')
        logger.info(f'generations: {generations}')
        logger.info(f'mutation_factor: {mutation_factor}')
        logger.info(f'crossover_rate: {crossover_rate}')
        logger.info(f'mutation_rate: {mutation_rate}')
        logger.info(f'mutation_range: {mutation_range}')
        logger.info(f'phi_p: {phi_p}')
        logger.info(f'phi_g: {phi_g}')
        logger.info(f'omega: {omega}')
        number_recorded += 1
    return ret

def bayes_run_fea(bounds, init_points=5, n_iter=25, sample_size=-1, noise_level = -1, func=-1):
    global best
    best = float('-inf')
    optimizer = BayesianOptimization(bayes_input_fea, bounds)
    optimizer.maximize(init_points, n_iter)

def bayes_input_base(
                generations=generations,
                pop_size=pop_size,
                mutation_factor=0.5,
                crossover_rate=0.9,
                mutation_rate=0.05,
                mutation_range=0.5,
                phi_p=math.sqrt(2),
                phi_g=math.sqrt(2),
                omega=1/math.sqrt(2),
                dim = 10
                ):
    dim = int(dim)
    generations = int(generations)
    pop_size = int(pop_size)

    domain = np.zeros((dim,2))
    domain[:,0] = 0
    domain[:,1] = 1

    global best
    global number_recorded

    if base_alg is feareu.ParallelBsplineFeaPSO:
        objective = base_alg(function=fitness, generations=generations, domain=domain, pop_size=pop_size, phi_p=phi_p, phi_g=phi_g, omega=omega, processes=processes, chunksize=chunksize)
        ret = -objective.run()
        if ret > best:
            best = ret
            results_dir = Path('results')
            results_dir.mkdir(parents=True, exist_ok=True)
            filename = results_dir / f"Function_{number_recorded}.png"
            plt.figure()
            objective.diagnostic_plots()
            plt.savefig(filename)
            logger.info(f'NEW BEST - NUMBER {number_recorded} ------------------------------------------------')
            logger.info(f'fitness evaluation: {ret}')
            logger.info(f'dim: {dim}')
            logger.info(f'base_alg: {base_alg.__name__}')
            logger.info(f'pop_size: {pop_size}')
            logger.info(f'generations: {generations}')
            logger.info(f'phi_p: {phi_p}')
            logger.info(f'phi_g: {phi_g}')
            logger.info(f'omega: {omega}')
            knots = base_alg.best_position

    elif base_alg is feareu.ParallelBsplineFeaDE:
        objective = base_alg(function = fitness, generations=generations, domain=domain, pop_size=pop_size, mutation_factor=mutation_factor, crossover_rate=crossover_rate, processes=processes, chunksize=chunksize)
        ret = -objective.run()
        if ret > best:
            best = ret
            results_dir = Path('results')
            results_dir.mkdir(parents=True, exist_ok=True)
            filename = results_dir / f"Function_{number_recorded}.png"
            plt.figure()
            objective.diagnostic_plots()
            plt.savefig(filename)
            logger.info(f'NEW BEST - NUMBER {number_recorded} ------------------------------------------------')
            logger.info(f'fitness evaluation: {ret}')
            logger.info(f'dim: {dim}')
            logger.info(f'base_alg: {base_alg.__name__}')
            logger.info(f'pop_size: {pop_size}')
            logger.info(f'generations: {generations}')
            logger.info(f'mutation_factor: {mutation_factor}')
            logger.info(f'crossover_rate: {crossover_rate}')
            knots = base_alg.best_position

    elif base_alg is feareu.ParallelBsplineFeaGA:
        objective = base_alg(function = fitness, generations=generations, domain=domain, pop_size=pop_size, mutation_rate=mutation_rate, mutation_range=mutation_range, processes=processes, chunksize=chunksize)
        ret = -objective.run()
        if ret > best:
            best = ret
            results_dir = Path('results')
            results_dir.mkdir(parents=True, exist_ok=True)
            filename = results_dir / f"Function_{number_recorded}.png"
            plt.figure()
            objective.diagnostic_plots()
            plt.savefig(filename)
            logger.info(f'NEW BEST - NUMBER {number_recorded} ------------------------------------------------')
            logger.info(f'fitness evaluation: {ret}')
            logger.info(f'dim: {dim}')
            logger.info(f'base_alg: {base_alg.__name__}')
            logger.info(f'pop_size: {pop_size}')
            logger.info(f'generations: {generations}')
            logger.info(f'mutation_rate: {mutation_rate}')
            logger.info(f'mutation_range: {mutation_range}')
            knots = base_alg.best_position

    number_recorded += 1
    return ret

def bayes_run_base(bounds, init_points=5, n_iter=25, sample_size=-1, noise_level=-1, func=-1):
    global best
    best = float('-inf')
    optimizer = BayesianOptimization(bayes_input_base, bounds)
    optimizer.maximize(init_points, n_iter)

def plot_results(knots, alg):
    bsp = splipy.BSplineBasis(3, knots, -1)
    xmat = bsp.evaluate(x, 0, True, True)
    xseq = np.linspace(0,1,len(y))
    xmat_seq = bsp.evaluate(xseq,0,True,True)
    xt = xmat.transpose()
    LHS = xt @ xmat
    RHS = xt @ y
    theta, info  = sparse.linalg.bicgstab(LHS, RHS)
    yest_seq = xmat_seq @ theta
    yest = xmat @ theta
    knot_y = np.zeros(knots.shape)
    knot_y[:] = np.min(y) - 0.2

    results_dir = Path('results')
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = results_dir / f"Baseline_{function.__name__}_noise_{n}_sample_size_{sample_size}"

    plt.figure()
    plt.plot(xseq,yest_seq,'y')
    plt.scatter(x,y,s=5)
    plt.scatter(knots,knot_y,color='orange', s=5)
    plt.savefig(filename)

    density = gaussian_kde(knots)
    xs = np.linspace(0,1,200)
    density.covariance_factor = lambda : .1
    density._compute_covariance()
    plt.figure()
    plt.plot(xs,density(xs))
    upper = np.max(density(xs))
    plt.ylim((0,upper))
    plt.savefig('results/doppler_ga_density.png')

    plt.figure()
    pso_alg.diagnostic_plots()
    plt.savefig('results/doppler_diagnostic_ga.png')



#Stuff for B-spline experimentation in particular
benchmarks = [feareu.big_spike, feareu.discontinuity, feareu.cliff, feareu.smooth_peak, feareu.second_smooth_peak, feareu.doppler]
sample_sizes = np.around(np.geomspace(2000, 200000, num=3)).astype(int)
base_algo_types = [
        feareu.ParallelBsplineFeaPSO,
        feareu.ParallelBsplineFeaDE,
        feareu.ParallelBsplineFeaGA
        ]
search_types = [
        feareu.ParallelBsplineFeaPSO,
        feareu.ParallelBsplineFeaDE,
        feareu.ParallelBsplineFeaGA
        ]
bounding = [
        pso_bounds,
        de_bounds,
        ga_bounds
        ]

#TODO: change this when we get a better bspline evaluation method
bspline_eval_class = feareu.SlowBsplineEval

if __name__ == '__main__':
    global x
    global y
    global base_alg
    for f, function in enumerate(benchmarks):
        for sample_size in sample_sizes:
            x = np.random.random(sample_size)
            y = function(x)
            func_width = np.max(y) - np.min(y)
            noises = np.linspace(func_width/100,func_width/20,num=5)
            for n, noise in enumerate(noises):
                y = feareu.make_noisy(y, noise)
                global fitness
                results_dir = Path('results')
                results_dir.mkdir(parents=True, exist_ok=True)
                filename = results_dir / f"Baseline_{function.__name__}_noise_{n}_sample_size_{sample_size}"
                xseq = np.linspace(0,1,100000)
                yseq = function(xseq)
                plt.figure()
                plt.scatter(x,y,'b')
                plt.plot(xseq,yseq,'k')
                plt.savefig(filename)
                fitness = bspline_eval_class(x, y)
                for i, algo in enumerate(base_algo_types):
                    base_alg = algo
                    bounds = deepcopy(pbounds)
                    bounds.update(bounding[i])
                    print("function: ", function, "\nsample size: ", sample_size, "\nnoise: ", noise, "\nalgorithm: FEA", algo)
                    bayes_run_fea(bounds, init_points=20, n_iter=100, sample_size=sample_size, noise_level = n, func = f)
                for i, algo in enumerate(search_types):
                    base_alg = algo
                    bounds = deepcopy(base_bounds)
                    bounds.update(bounding[i])
                    print("function: ", function, "\nsample size: ", sample_size, "\nnoise: ", noise, "\nalgorithm: ", algo)
                    bayes_run_base(bounds, init_points=20, n_iter=100, sample_size=sample_size, noise_level = n, func = f)
