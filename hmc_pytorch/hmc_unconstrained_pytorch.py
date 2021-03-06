""" Numpy implementations of unconstrained Euclidean metric HMC samplers. """

import numpy as np
import torch
from numpy import inf
import scipy.linalg as la
from hmc_base_pytorch import AbstractHmcSampler


class IsotropicHmcSampler(AbstractHmcSampler):
    """Standard unconstrained HMC sampler with identity mass matrix. """

    def kinetic_energy(self, pos, mom, mass, cache={}):
        mom = mom.cuda()
        if mass.shape[0]==1:
            return (0.5 * mom*mom)/mass
        else:
            mass_inv = torch.inverse(mass).cuda()
            #print("mom: "+str(mom.is_cuda))
            #print("mass_inv: "+str(mass_inv.is_cuda))
            return 0.5*((mom@mass_inv)@mom)
            #return 0.5*torch.mm(torch.mm(mom, mass_inv), mom)
            #return 0.5 * mom.dot(mass_inv).dot(mom)
            
    def simulate_dynamic(self, n_step, dt, pos, mom, mass, cache={}):
        if mass.shape[0]==1:
            
            #print("pos:"+str(pos)+" "+str(pos.requires_grad))
            grad = self.energy_grad(pos, cache)
            
            #print("pos: "+str(pos))
            #print("grad :"+str(grad))
            #print("mom"+str(mom))
           
            mom = mom - 0.5 * dt * grad
            mom = mom.cuda()
            pos = pos.cuda()
            pos = pos + dt * (mom/mass)
            for s in range(1, n_step):
                #print("loop pos: "+str(pos))
                tmp = self.energy_grad(pos, cache)
                #print("loop grad: "+str(tmp))
                mom = mom - dt * tmp
                pos = pos + dt * (mom/mass)
            mom = mom - 0.5 * dt * self.energy_grad(pos, cache)
            return pos, mom, None
                
        else:
            mom = mom.cuda()
            pos = pos.cuda()
            mass_inv = torch.inverse(mass).cuda()
            
            tmp = self.energy_grad(pos, cache).cuda()
            #print("pos: "+str(pos))
            #print("grad: "+str(tmp))
            #mom = mom - 0.5 * dt * self.energy_grad(pos, cache)
            #print("tmp: "+str(tmp.shape))
            #print("mom: "+str(mom.shape))
            #print("dt: "+str(dt.shape))
            
            mom = mom - 0.5 * dt * tmp
            #print("mom size: "+str(mom.shape))
            #print("mom: "+str(mom.is_cuda))
            #print("mass_inv: "+str(mass_inv.is_cuda))
            #print("pos: "+str(pos.is_cuda))
            pos = pos + dt * (mom@mass_inv)
            #print("2nd pos: "+str(pos))
            for s in range(1, n_step):
                #print("loop pos: "+str(pos))
                tmp = self.energy_grad(pos, cache).cuda()
                #print("loop grad: "+str(tmp))
                mom = mom - dt * tmp
                pos = pos + dt * (mom@mass_inv)
            mom = mom - 0.5 * dt * (self.energy_grad(pos, cache).cuda())
            return pos, mom, None

    def sample_independent_momentum_given_position(self, pos, cache={}):
        t = torch.Tensor(pos.shape[0])
        t.normal_()
        t.requires_grad=True
        #print("mom: "+str(t))
        #print("============"+str(self.dtype))
        #x = self.prng.normal(size=pos.shape[0]).astype(self.dtype)
        #print(x)
        #print("t: "+str(t))
        return t

