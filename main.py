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

from instance import Instance
from gui import show_instance



def test_domain():
	instance = Instance("instances/p01")
	genotype = [ (0,0), (40, 20), (20, 40), (50, 50) ]

	print("\nRunning test_domain..")
	from domainalgo import construct_route, get_closest_depots

	rand = random.Random(2)


	depots = get_closest_depots(instance, genotype, rand)

	assert depots[0].id == 0
	assert depots[1].id == 2
	assert depots[2].id == 1
	assert depots[3].id == 3

	print('Passed.\n')

	r = construct_route(instance, genotype, rand)



if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("You need to specify an instance file.");
		sys.exit(1)

	if '-t' in sys.argv or '--test' in sys.argv:
		test_domain()
		sys.exit(0)

	inputfile = sys.argv[1]

	instance = Instance(inputfile)

	#show_instance(instance)

