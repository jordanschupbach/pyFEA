import numpy as np
import matplotlib.pyplot as plt

class DE:
    """Differential Evolution Algorithm."""
    def __init__(
        self,
        function,
        domain,
        generations=100,
        pop_size=20,
        mutation_factor = 0.5,
        crossover_rate = 0.9
    ):
        """
        @param function: the objective function to be minimized.
        @param domain: the domain on which we explore the function stored as a (dim,2) matrix,
        where dim is the number of dimensions we evaluate the function over.
        @param generations: the number of generations run before the algorithm terminates.
        @param pop_size: the number of individuals in the population.
        @param mutation_factor: the scalar factor used in the mutation step.
        @param crossover_rate: the probability of taking a mutated value during the crossover step.
        """
        self.generations = generations
        self.pop_size = pop_size
        self.func = function
        self.domain = domain
        self.pop = self.init_pop()
        self.pop_eval = [self.func(self.pop[i]) for i in range(self.pop_size)]
        self.fitness_functions = self.pop_size
        self.best_eval = np.min(self.pop_eval)
        self.best_solution = np.copy(self.pop[np.argmin(self.pop_eval),:])
        self.mutation_factor = mutation_factor
        self.crossover_rate = crossover_rate
        self.mutant_pop = np.zeros((self.pop_size, self.domain.shape[0]))
        self.ngenerations = 0
        self.average_pop_variance = []
        self.average_pop_eval = []
        self.fitness_list = []
        self.best_answers = []

    def init_pop(self):
        """
        Randomly initializes the values of the population as a numpy array of shape (pop_size, dim).
        """
        lbound = self.domain[:, 0]
        area = self.domain[:, 1] - self.domain[:, 0]
        return lbound + area * np.random.random(size=(self.pop_size, area.shape[0]))

    def run(self):
        """
        Run the minimization algorithm.
        """
        for gen in range(self.generations):
            #print("generation: ", gen, "/", self.generations)
            self.ngenerations += 1
            self.mutate()
            self.stay_in_domain()
            self.crossover()
            self.selection()
            self._track_vals()
        return  self.best_eval

    def mutate(self):
        """
        The mutation step. Stores mutant values in self.mutant_pop.
        """
        for i in range(self.pop_size):
            idxs = np.random.choice(self.pop_size, size = 3, replace = False)
            new_pop_mem = self.pop[i,:]+self.mutation_factor*(self.pop[idxs[0],:] - self.pop[idxs[1],:] + self.pop[idxs[2],:])
            self.mutant_pop[i,:] = new_pop_mem

    def crossover(self):
        """
        The crossover step. Stores crossover values in self.mutant_pop.
        """
        for i in range(self.pop_size):
            cross_rand = np.round(np.random.choice([0,1], p=[1-self.crossover_rate, self.crossover_rate], size=self.domain.shape[0]))
            crossed_guy = np.where(cross_rand==1, self.pop[i,:], self.mutant_pop[i,:])
            self.mutant_pop[i,:] = crossed_guy

    def selection(self):
        """
        The fitness evaluation and selection. Greedily selects whether to keep or throw out a value.
        Consider implementing and testing more sophisticated selection algorithms.
        """
        for i in range(self.pop_size):
            fella_eval = self.func(self.mutant_pop[i,:])
            self.fitness_functions+=1
            if fella_eval < self.pop_eval[i]:
                self.pop_eval[i] = fella_eval
                self.pop[i,:] = np.copy(self.mutant_pop[i,:])
        self.best_solution = np.copy(self.pop[np.argmin(self.pop_eval),:])
        self.best_eval = np.min(self.pop_eval)

    def stay_in_domain(self):
        """
        Ensure that the mutated population doesn't move outside the domain of our function by projecting
        them to the domain's boundary at that point.
        """
        self.mutant_pop = np.where(self.domain[:, 0] > self.mutant_pop, self.domain[:, 0], self.mutant_pop)
        self.mutant_pop = np.where(self.domain[:, 1] < self.mutant_pop, self.domain[:, 1], self.mutant_pop)

    def _track_vals(self):
        self.average_pop_eval.append(np.average(self.pop_eval))
        self.average_pop_variance.append(np.average(np.var(self.pop, axis = 0)))
        self.fitness_list.append(self.fitness_functions)
        self.best_answers.append(self.best_eval)
    
    def diagnostic_plots(self):
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3)

        ax1.plot(self.fitness_list, self.average_pop_variance)
        ax1.set_xlabel('# fitness evaluations', fontsize=10)
        ax1.set_ylabel('population variance', fontsize=10)
        ax1.set_title('Population Diversity', fontsize=10)

        ax2.plot(self.fitness_list, self.average_pop_eval)
        ax2.set_xlabel('# fitness evaluations', fontsize=10)
        ax2.set_ylabel('average MSE', fontsize=10)
        ax2.set_title('Average Solution Fitness', fontsize=10)

        ax3.plot(self.fitness_list, self.best_answers)
        ax3.set_xlabel('# fitness evaluations', fontsize=10)
        ax3.set_ylabel('best MSE', fontsize=10)
        ax3.set_title('Best Solution Fitness', fontsize=10)

        fig.suptitle("DE")
        fig.tight_layout()