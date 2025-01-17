import numpy as np

from pyfea.base_algos import DE, parallel_eval
from pyfea.fea.base_algos.fea_base_algo import FeaBaseAlgo


class FeaDE(DE, FeaBaseAlgo):
    """
    The Differential Evolution algorithm set up for use in an FEA.
    See the base Differential Evolution algorithm in de.py for the full functionality.
    """

    def get_solution_at_index(self, idx):
        """
        The method to retrieve a variable's value from the base algorithm.
        @param idx: the index of the variable to be retrieved.
        """
        return self.best_solution[idx]

    def update_worst(self, context):
        """
        The second half of the share step in the FEA algorithm, where we update
        the worst individual in our population to become the context vector.
        @param context: the context vector of our FEA.
        """
        self.pop[np.argmax(self.pop_eval), :] = context

    @classmethod
    def from_kwargs(cls, function, domain, params):
        """
        The method for inputting parameters to the DE from FEA.
        @param function: the objective function to minimize.
        @param domain: the domain over which to minimize as a numpy array of size (dim, 2)
        @param params: the remaining parameters, namely generations, pop_size, mutation_factor,
        and crossover_rate. These are taken in as a dictionary here from the keyword arguments
        passed to FEA's constructor.
        """
        kwargs = {
            "generations": 100,
            "pop_size": 20,
            "mutation_factor": 0.5,
            "crossover_rate": 0.5,
            "fitness_terminate": False
        }
        kwargs.update(params)
        return cls(
            function=function,
            domain=domain,
            generations=kwargs["generations"],
            pop_size=kwargs["pop_size"],
            mutation_factor=kwargs["mutation_factor"],
            crossover_rate=kwargs["crossover_rate"],
            fitness_terminate=kwargs["fitness_terminate"]
        )

    def run(self, progress=False, parallel=False, processes=4, chunksize=4):
        """
        Run the base algorithm.
        """
        return super().run(progress, parallel, processes, chunksize)

    def update_bests(self, parallel=False, processes=4, chunksize=4):
        """
        Update the evaluation of the objective function after a context vector update.
        """
        if not parallel:
            self.pop_eval = [self.func(self.pop[i, :]) for i in range(self.pop_size)]
        else:
            self.pop_eval = parallel_eval(self.func, self.pop, processes, chunksize)
        self.nfitness_evals += self.pop_size
        self.best_solution = np.copy(self.pop[np.argmin(self.pop_eval), :])
        self.best_eval = np.min(self.pop_eval)

    def reinitialize_population(self):
        for particle in range(self.pop_size):
            for p in range(len(self.pop[0])):
                if (
                    self.pop[particle, p] < self.domain[:0].all()
                    or self.pop[particle, p] > self.domain[:1].all()
                ):
                    self.pop[particle, p] = (
                        self.domain[0, 0]
                        + (self.domain[0, 1] - self.domain[0, 0]) * np.random.random()
                    )

    def base_reset(self):
        """
        Reset the algorithm in preparation for another run.
        """
        self.reinitialize_population()
        self.update_bests()
