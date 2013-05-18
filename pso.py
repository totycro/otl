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


class Config:

	def __init__(self, num_particles):
		self.num_particles = num_particles



def pso(instance, rand, config):
	assert isinstance(instance, Instance)
	assert isinstance(config, Config)
	assert isinstance(rand, random_module.Random)

	population = list(create_starting_solution(instance, rand) for i in range(config.num_particles))

	pbest = list((i, sys.maxsize) for i in population) # best genotype + obj value

	gbest = 0, sys.maxsize # index of best pbest, will be reset before used
	best_phenotype = None

	# 2-dim vector for each starting location of each individual
	individual_velocities = [[[0,0] for i in population[0] ] for j in population]

	for it in range(30):

		print("\n\nIt", it,"\n")

		print("pop: ", end="\n")
		pprint(population)
		print("vel: ", end="\n")
		pprint(individual_velocities)
		print("pbest: ", end="\n")
		pprint(pbest)

		# check solutions
		for i, genotype in enumerate(population):

			location_velocities = individual_velocities[i]

			# apply velocities
			for j, location in enumerate(genotype):
				genotype[j] = (
				  location[0] + location_velocities[j][0],
				  location[1] + location_velocities[j][1]
				  )


			# possibly test phenotype better by randomising construction
			r = construct_routes(instance, genotype)
			r_opt =  two_opt(r)

			print("Sol",i,"obj naked:", get_objective_value(r), "; obj opt:", get_objective_value(r_opt))

			obj_val = get_objective_value(r_opt)

			if obj_val < pbest[i][1]:
				pbest[i] = (genotype, obj_val)

				print("\nNEW PBEST\n")

				if obj_val < pbest[gbest[0]][1]:
					gbest = (i, obj_val)
					best_phenotype = r_opt

			# update velocities
			for i, location_velocities in enumerate(individual_velocities):
				individual = population[i]
				gbest_sol = pbest[gbest[0]][0]
				pbest_sol = pbest[i][0]

				#print('move to', pbest_sol, ' and ', gbest_sol)

				accel = 0.3
				# velocity is a 2-dim vector for each staring location
				for j, velocity in enumerate(location_velocities):

					velocity[0] += \
						accel * rand.random() * (pbest_sol[j][0] - individual[j][0]) + \
						accel * rand.random() * (gbest_sol[j][0] - individual[j][0])

					velocity[1] += \
						accel * rand.random() * (pbest_sol[j][1] - individual[j][1]) + \
						accel * rand.random() * (gbest_sol[j][1] - individual[j][1])


		show_routes(instance, best_phenotype)
		#print_routes(r_opt)







