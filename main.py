#!/usr/bin/env python3

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
import random
import time

from instance import Instance
from pso import pso, Config
from gui import show_instance



def test_domain():
	instance1 = Instance("instances/p01")
	genotype = [ (0,0), (40, 20), (20, 40), (50, 50) ]

	print("\nRunning test_domain..")
	from domainalgo import construct_routes, _get_closest_depots, create_starting_solution, get_objective_value, two_opt, print_routes

	rand = random.Random(2)

	depots = _get_closest_depots(instance1, genotype)

	assert depots[0].id == 0
	assert depots[1].id == 2
	assert depots[2].id == 1
	assert depots[3].id == 3

	print('Passed.\n')

	#instance0 = Instance("instances/p23")

	#pso(instance0, rand, Config())

	"""
	genotype = create_starting_solution(instance0, rand)

	r = construct_routes(instance0, genotype)

	show_routes(instance0, r)
	print_routes(r)
	r = two_opt(r)
	print_routes(r)

	print(get_objective_value(r))

	show_routes(instance0, r)
	"""


def check_instance(outfile, instance_file, rand, iterations):
	phen = pso(Instance(instance_file), rand, Config(iterations))
	print("%s: %.2f (pen: %.2f, route: %.2f): %s" % \
	      (instance_file, phen.obj_value, phen.penalties, phen.route_cost, [[r.id for r in route] for route in phen.routes]), file=outfile)
	outfile.flush()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("You need to specify an instance file.")
		sys.exit(1)

	if len(sys.argv) < 3:
		print("You need to specify a rng seed.")
		sys.exit(1)

	seed = sys.argv[2]
	rand = random.Random(seed)

	if len(sys.argv) < 4:
		iterations = 20
	else:
		iterations = int(sys.argv[3])

	if '-t' in sys.argv or '--test' in sys.argv:
		test_domain()
		sys.exit(0)


	if '-a' in sys.argv:
		outfile = open("test.out", "a")
		outfile.write("Running tests (seed: %s, it: %d)\n" % (seed, iterations) )
		outfile.flush()
		#for inst in ("instances/p0%d" % d for d in ( 1, 2, 3, 4, 5 )):
		for inst in ("instances/p0%d" % d for d in range(10)):
			check_instance(outfile, inst, rand, iterations)
		for inst in ("instances/p0%d" % d for d in range(10, 24)):
			check_instance(outfile, inst, rand, iterations)
		sys.exit(0)

	inputfile = sys.argv[1]

	instance = Instance(inputfile)

	#pso(instance, rand, Config(iterations=iterations))




	#show_instance(instance)


