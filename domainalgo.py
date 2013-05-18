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
# 51 Franklin St,i Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from pprint import pprint
import heapq
import sys

from instance import Instance

dist_squared = lambda x, y: (x[0]-y[0])**2 + (x[1]-y[1])**2
dist = lambda x, y: ((x[0]-y[0])**2 + (x[1]-y[1])**2) ** 0.5

def print_routes(routes):
	print("Routes (obj:%s):"%get_objective_value(routes))
	for i, route in enumerate(routes):
		print(i, [r.id for r in route])
	print()

def get_objective_value(routes):
	"""Calculate objective value for a set of routes."""
	obj_value = 0
	for route in routes:
		for i in range(len(route)-1):
			obj_value += dist(route[i].pos, route[i+1].pos)
	return obj_value


def create_starting_solution(instance, rand):
	"""Creates initial genotypes"""
	assert isinstance(instance, Instance)
	return list(
	  ( rand.randint(instance.min_point[0], instance.max_point[0]+1),
	    rand.randint(instance.min_point[1], instance.max_point[1]) )
	  for i in range(instance.num_vehicles) )



def construct_routes(instance, genotype):
	"""Create phenotype from genotype."""
	assert isinstance(instance, Instance)
	# genotype contains base points

	# find closest depots
	vehicle_depots = _get_closest_depots(instance, genotype)

	routes = list([i] for i in vehicle_depots ) # list of routes with starting state

	vehicle_loads = [0] * len(routes)
	vehicle_route_duration = [0] * len(routes)

	# multiple nearest neighbor:
	# construct all routes at the same time. connect where dist to base point
	# plus current pos is minimal.

	customers_to_visit = set(instance.customers)
	customers_visited = set()

	neighbors_per_vehicle = [[]] * len(routes) # heap of neighbors per vehicle sorted by distance


	def calculate_neighbors_per_vehicle(vehicle):
		"""Calculate heuristic value of all open customers of vehicle i, considering cur loc and genotype, return as heap"""
		route = routes[vehicle]

		# constraints per depot (but same in file usually)
		max_vehicle_load = route[0].max_vehicle_load
		max_route_duration = route[0].max_route_duration

		#print('veh ', i, route[-1], genotype[i])
		l = []
		for customer in customers_to_visit:

			if vehicle_loads[vehicle] + customer.demand > max_vehicle_load:
				continue # too much to carry

			# dist from cur pos and from base point (genotype)
			route_dist = dist(route[-1].pos, customer.pos)

			# check if we go there, then home, if we're still in the max allowed time
			if vehicle_route_duration[vehicle] + route_dist + dist(customer.pos, route[0].pos) > max_route_duration:
				continue # can't do this


			dist_value = route_dist + dist(genotype[vehicle], customer.pos)
			heapq.heappush(l, (dist_value, route_dist, vehicle, customer)) # add vehicle id, makes it easier later

		#pprint(l)
		#print()
		if not l:
			l.append((sys.maxsize,)) # HACK: never the least value
		return l


	# init neightbors per vehicle
	for i in range(len(routes)):
		neighbors_per_vehicle[i] = calculate_neighbors_per_vehicle(i)

	# pick best one

	"""
	pprint([i[0] for i in neighbors_per_vehicle])
	print()
	pprint(min([i[0] for i in neighbors_per_vehicle]))
	"""

	while customers_to_visit:		"""
		pprint(customers_to_visit)
		print_routes(routes)
		pprint(neighbors_per_vehicle)
		pprint(vehicle_loads)
		pprint(vehicle_route_duration)
		"""

		candidate = min([i[0] for i in neighbors_per_vehicle])
		if candidate[0] == sys.maxsize:
			# TODO: what to do in case of no valid solution?
			break

		_, route_dist, vehicle, customer = candidate
		neighbors_per_vehicle[vehicle] = calculate_neighbors_per_vehicle(vehicle)
		# customer might already have been visited by other vehicle, we don't drop these values from other lists
		if customer not in customers_visited:
			# use it
			routes[vehicle].append(customer)
			customers_to_visit.remove(customer)
			customers_visited.add(customer)
			#print('veh', vehicle, ' serves ', customer)

			vehicle_loads[vehicle] += customer.demand
			vehicle_route_duration[vehicle] += route_dist

	for route in routes:
		route.append(route[0])

	return routes


def _get_closest_depots(instance, genotype):
	"""Returns the closest depots for the genotype values. Currently unrandomized."""
	closest_depots=[]

	for vehicle_base in genotype:
		#pprint.pprint(list( ( ( (vehicle_base[0]-d.pos[0])**2 + (vehicle_base[1]-d.pos[1])**2 ), d_id) for (d_id, d) in enumerate(instance.depots) ) )

		# use squared dist
		closest = min( (dist_squared(vehicle_base, d.pos), d_id) for (d_id, d) in enumerate(instance.depots) )

		closest_depots.append( instance.depots[ closest[1] ] )

	return closest_depots



def two_opt(routes):
	"""Do exhaustive 2-opt, return new route"""

	# NOTE: ensure not to introduce a constraint violation.
	# (doesn't change load)
	def do_route(route): # return new route
		# don't change depot
		for i in range(0, len(route)-2):
			u_1 = route[i].pos
			u_2 = route[i+1].pos
			for j in range(i+1, len(route)-1):
				v_1 = route[j].pos
				v_2 = route[j+1].pos

				if ( dist_squared(u_1, u_2) + dist_squared(v_1, v_2) ) > \
				   ( dist_squared(u_1, v_1) + dist_squared(u_2, v_2) ):
					# is better, put v_1 after u_1, then in reverse order until u_2, then v_2

					# TODO: do in place?
					route_prime = route[:i+1] + list(reversed(route[i+1:j+1])) + route[j+1:]
					return do_route(route_prime)

		return route # nothing found

	return list(do_route(route) for route in routes)


