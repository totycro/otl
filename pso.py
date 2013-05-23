# ###################################################
# Copyright (C) 2013 Bernhard Mallinger
#
# This file is part of otl-prog
#
# otl-prog is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import sys
from pprint import pprint

import random as random_module

from instance import Instance
from domainalgo import create_starting_solution, get_objective_value, construct_routes, two_opt, print_routes
from gui import show_routes
from utils import pprint_list_of_list_of_floats, pprint_list_of_floats

from utils import pprint_list_of_list_of_floats as pll, pprint_list_of_floats as pl

class Config:
	DURATION_EXCEEDED_PENALTY = 100
	LOAD_EXCEEDED_PENALTY = 100
	NUM_PARTICLES = 8

	REBUILD_KDTREE_DEAD_CUSTOMERS_THRESHOLD = 0.75
	NEARBY_CUSTOMERS_TO_CHECK = 15

	def __init__(self, iterations):
		self.iterations = iterations


class Phenotype:
	def __init__(self, genotype, routes, route_cost, route_penalties, load_penalties):
		self.genotype = genotype
		self.routes = routes
		self.route_cost = route_cost
		self.route_penalties = route_penalties
		self.load_penalties = load_penalties

	def local_search(self, config, optimal=False):
		self.routes = two_opt(self.routes, 5 if not optimal else -1) # limit to 5 exchanges
		self.route_cost, self.route_penalties = get_objective_value(self.routes, config)

	@property
	def penalties(self):
		return self.route_penalties + self.load_penalties

	@property
	def obj_value(self):
		return self.route_cost + self.penalties

	def __str__(self):
		return "Phenotype(route_cost=%s,penalties=%s)" % (self.route_cost, self.penalties)

def pso(instance, rand, config):
	assert isinstance(instance, Instance)
	assert isinstance(config, Config)
	assert isinstance(rand, random_module.Random)

	population = list(create_starting_solution(instance, rand) for i in range(config.NUM_PARTICLES))

	pbest = list((i, sys.maxsize) for i in population) # best genotype + obj value

	gbest = 0, sys.maxsize # index of best pbest, will be reset before used
	best_phenotype = None

	# 2-dim vector for each starting location of each individual
	individual_velocities = [[[0,0] for i in population[0] ] for j in population]

	for it in range(config.iterations):
		print("\n\nIt", it,"\n")

		"""
		print("pop: ", end="\n")
		pprint_list_of_list_of_floats(population)
		print("vel: ", end="\n")
		pprint_list_of_list_of_floats(individual_velocities)
		print("pbest: ", end="\n")
		pprint(pbest, width=200)
		#"""

		# check solutions

		#if it != 0: import pdb ; pdb.set_trace()

		for individual_id, genotype in enumerate(population):
			location_velocities = individual_velocities[individual_id]

			# apply velocities
			for j, location in enumerate(genotype):
				genotype[j] = (
				  location[0] + location_velocities[j][0],
				  location[1] + location_velocities[j][1]
				  )

			# possibly test phenotype better by randomising construction
			phenotype = construct_routes(instance, genotype, config)
			phenotype.local_search(config)

			if phenotype.obj_value < pbest[individual_id][1]:
				pbest[individual_id] = (genotype, phenotype.obj_value)

				#print("\nNEW PBEST %s pen:%s\n" % (phenotype.obj_value, phenotype.penalties))

				if phenotype.obj_value < gbest[1]:
					gbest = (individual_id, phenotype.obj_value)
					best_phenotype = phenotype

					print("\nNEW GBEST")
					#import pdb ; pdb.set_trace()
					best_phenotype.local_search(config, optimal=True)

					print_routes(best_phenotype)
					#show_routes(instance, best_phenotype)

		# update velocities
		#if it == 8: import pdb ; pdb.set_trace()
		for individual_id, location_velocities in enumerate(individual_velocities):
			individual = population[individual_id]
			gbest_sol = pbest[gbest[0]][0]
			pbest_sol = pbest[individual_id][0]

			#print('move to', pbest_sol, ' and ', gbest_sol)

			accel =.2
			accel_g = .3 * accel
			accel_p = .2 * accel

			# velocity is a 2-dim vector for each staring location
			for loc_id, velocity in enumerate(location_velocities):
				old_vel = velocity[:]

				velocity[0] += \
					accel_p * rand.random() * (pbest_sol[loc_id][0] - individual[loc_id][0]) + \
					accel_g * rand.random() * (gbest_sol[loc_id][0] - individual[loc_id][0])

				velocity[1] += \
					accel_p * rand.random() * (pbest_sol[loc_id][1] - individual[loc_id][1]) + \
					accel_g * rand.random() * (gbest_sol[loc_id][1] - individual[loc_id][1])

				if individual_id == 0 and loc_id == 0:
					print('accel ', (velocity[0]-old_vel[0], velocity[1]-old_vel[1]), ' to ', velocity)
					pass


		if False or it % 5 == 0 and it != 0:
			#show_routes(instance, best_phenotype)
			pass









