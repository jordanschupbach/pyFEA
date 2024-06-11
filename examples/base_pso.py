import math
from copy import deepcopy
import numpy as np


def rastrigin(x):
    A = 10
    n = len(x)
    return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))



class DummyFunc():

    def __init__(self, function):
        self.func = function

    def __call__(self, input):
        output = self.func(input)
        return output

class PSO():
    def __init__(self, function, domain, generations=100, pop_size=20, phi_p=math.sqrt(2), phi_g=math.sqrt(2), omega=1/math.sqrt(2)):
        self.generations = generations
        self.pop_size = pop_size
        self.func = function
        self.domain = domain
        self.phi_p = phi_p
        self.phi_g = phi_g
        self.omega = omega
        self.pop = self.init_pop()
        self.pbest = self.pop
        self.pbest_eval = [self.func(self.pop[i, :]) for i in range(self.pop_size)]
        self.gbest_eval = np.min(self.pbest_eval)
        self.gbest = self.pbest[np.argmin(self.pbest_eval),:]
        self.velocities = self.init_velocities()

    @classmethod
    def from_kwargs(cls, function, domain, input):
        kwargs = {'generations':100, 'pop_size':20,'phi_p':math.sqrt(2),'phi_g':math.sqrt(2),'omega':1/math.sqrt(2)}
        kwargs.update(input)
        return cls(function = function, domain = domain, generations=kwargs['generations'],pop_size=kwargs['pop_size'],phi_p=kwargs['phi_p'],phi_g=kwargs['phi_g'],omega=kwargs['omega'])

    def init_pop(self):
        lbound = self.domain[:,0]
        area = self.domain[:,1] - self.domain[:,0]
        return lbound + area * np.random.random(size=(self.pop_size, area.shape[0]))

    def init_velocities(self):
        area = self.domain[:,1] - self.domain[:,0]
        return 0.5 * area * np.random.random(size=(self.pop_size, area.shape[0]))
    
    def run(self):
        for gen in range(self.generations):
            print("iter: ", gen, "/", self.generations)
            self.update_velocities()
            self.pop = self.pop + self.velocities
            self.stay_in_domain()
            self.update_bests()
        return self.gbest

    
    def stay_in_domain(self):
        #print("pre-domain check: ", self.pop)
        self.pop = np.where(self.domain[:,0]>self.pop, self.domain[:,0], self.pop)
        #print("post-lbound check: ", self.pop)
        self.pop = np.where(self.domain[:,1]<self.pop, self.domain[:,1], self.pop)
        #print("post-domain check: ", self.pop)

    def update_velocities(self):
        r_p = np.random.random(size=self.pop.shape)
        r_g = np.random.random(size=self.pop.shape)
        self.velocities = self.omega * self.velocities + self.phi_p * r_p * (self.pbest - self.pop) + self.phi_g * r_g * (self.gbest - self.pop)

    def update_bests(self):
        for pidx in range(self.pop_size):
            curr_eval = self.func(self.pop[pidx,:])
            if curr_eval < self.pbest_eval[pidx]:
                self.pbest[pidx, :] = self.pop[pidx,:]
                self.pbest_eval[pidx] = curr_eval
                if curr_eval < self.gbest_eval:
                    print("updating gbest from ", self.gbest_eval, " to ", curr_eval)
                    self.gbest = (self.pop[pidx,:])
                    self.gbest_eval = curr_eval

"""input_func = DummyFunc(rastrigin)
kwargs = {"function":rastrigin, "domain":np.array([[-5,5],[-5,5]]), "generations":200, "pop_size":20, "phi_p":1, "phi_g":math.sqrt(2), "omega":1/math.sqrt(2)}
pso = PSO(function=rastrigin, domain=np.array([[-5,5],[-5,5]]))
pso.run()
print(pso.phi_p)
pso = PSO(input_func, np.array([[-5,5],[-5,5]]))
pso.run()

def main():
    array = np.zeros((10))
    array[0] = 1
    array[1] = 2
    domain = np.zeros((2, 2))
    domain[:,0] = -5
    domain[:,1] = 5
    function = Function(array, rastrigin__, [0, 1])
    pso = PSO(function, domain)
    print(pso.run())
if __name__ == "__main__":
    main()"""
