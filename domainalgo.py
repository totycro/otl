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
import itertools
import sys
from scipy.spatial import cKDTree as KDTree

from instance import Instance
from utils import dist, dist_squared

def print_routes(phenotype):
	routes = phenotype.routes
	print("Routes (obj:%s; pen:%s):"%(phenotype.route_cost, phenotype.penalties))
	for i, route in enumerate(routes):
		print(i, [r.id for r in route])
	print()

def get_objective_value(routes, config):
	"""Calculate objective value for a set of routes."""
	obj_value = 0
	route_penalties = 0
	for route in routes:
		route_val = 0

		for i in range(len(route)-1):
			route_val += dist(route[i].pos, route[i+1].pos)

		obj_value += route_val

		max_duration = route[0].max_route_duration

		if max_duration > 0 and route_val > max_duration:
			route_penalties += (route_val - max_duration) * config.DURATION_EXCEEDED_PENALTY
	return obj_value, route_penalties


def create_starting_solution(instance, rand):
	"""Creates initial genotypes"""
	assert isinstance(instance, Instance)

	# old code :

	"""
	return list(
		( rand.randint(instance.min_point[0], instance.max_point[0]+1),
			rand.randint(instance.min_point[1], instance.max_point[1]) )
	return list(
		for i in range(instance.num_vehicles_per_depot * instance.num_depots) )
	"""


	# new code:


	def get_positions_for_depot(depot):
		other_depots = instance.depots[:]
		other_depots.remove(depot)
		#nearest_depot_dist, nearest_depot = min( (dep_dist, other_dep) for (dep_dist, other_dep) in list( ( dist(depot.pos, o.pos), o ) for o in other_depots ) )

		nearest_depot_dist_x = min( abs(depot.pos[0] - d.pos[0]) for d in other_depots )
		nearest_depot_dist_y = min( abs(depot.pos[1] - d.pos[1]) for d in other_depots )
		for i in range(instance.num_vehicles_per_depot):
			yield (depot.pos[0] + (rand.random() - 1) * nearest_depot_dist_x, \
						 depot.pos[1] + (rand.random() - 1) * nearest_depot_dist_y)


	ret = []

	for d in instance.depots:
		ret.extend( (pos for pos in get_positions_for_depot(d) ) )

	return ret



def construct_routes(instance, genotype, config, rand):
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

	class AlgoData:
		def __init__(self, instance):
			self.customers_to_visit = set(instance.customers) # don't reassign
			self.customers_visited = set() # don't reassign
			self.rebuild_kdtree()
			assert isinstance(self.kdtree, KDTree)

		def rebuild_kdtree(self):
			"""Builds a new kd-tree (as we can't remove nodes, do this sometimes to not have too many dead nodes)"""
			customers_fixed_order = list(self.customers_to_visit) # will need copy anyway to have unchanging indices
			self.kdtree = KDTree([i.pos for i in customers_fixed_order])
			self.kdtree_customers = customers_fixed_order
			#print('rebuild kdtree, nodes:', len(customers_fixed_order))

	data = AlgoData(instance) # don't reassign

	neighbors_per_vehicle = [[]] * len(routes) # heap of neighbors per vehicle sorted by distance

	def calculate_neighbors_per_vehicle(vehicle):
		"""Calculate heuristic value of all open customers of vehicle i, considering cur loc and genotype, return as heap"""
		route = routes[vehicle]

		# constraints per depot (but same in file usually)
		max_vehicle_load = route[0].max_vehicle_load
		max_route_duration = route[0].max_route_duration

		#print('veh ', i, route[-1], genotype[i])
		l = []

		# get 10 nearest points from route
		# TODO: also from base point?
		num_nodes = min(config.NEARBY_CUSTOMERS_TO_CHECK, len(data.kdtree_customers))
		distances, customer_indices = data.kdtree.query(route[-1].pos, num_nodes)

		if num_nodes == 1: # return format different, fix it
			distances = [ distances ]
			customer_indices = [ customer_indices ]

		#print(customer_indices)
		dead_customers = 0

		for customer_index in range(len(customer_indices)):
			customer = data.kdtree_customers[customer_index]

			if customer in data.customers_visited:
				dead_customers += 1
				continue

			route_penalty = 0
			load_penalty = 0

			if max_vehicle_load > 0:
				to_carry = vehicle_loads[vehicle] + customer.demand
				if to_carry >  max_vehicle_load:
					# we have to value the overfullness in terms of distance here
					# do it in terms of diagonal lenghts

					overload = to_carry - max_vehicle_load
					if overload > customer.demand:
						overload = customer.demand # rest has been punished before

					# +100% costs 10 diagonals
					load_penalty += (overload / max_vehicle_load) * config.LOAD_EXCEEDED_PENALTY * instance.diagonal_length

			# dist from cur pos and from base point (genotype)
			#route_dist = dist(route[-1].pos, customer.pos)
			# with kd-tree, is given by it:
			route_dist = distances[customer_index]

			if max_route_duration > 0:
				# check if we go there, then home, if we're still in the max allowed time
				dist_customer_home = dist(customer.pos, route[0].pos)
				duration = vehicle_route_duration[vehicle] + route_dist + dist_customer_home
				if duration > max_route_duration:
					# punish additional distance by 10 times the amount
					# overflow now contains the path back to home, which isn't actually taken yet, so don't punish it yet
					overflow = duration - max_route_duration - dist_customer_home
					if overflow > 0:
						route_penalty += overflow * config.DURATION_EXCEEDED_PENALTY


			dist_value = route_dist + dist(genotype[vehicle], customer.pos) + load_penalty + route_penalty
			heapq.heappush(l, (dist_value, route_dist, route_penalty, load_penalty, vehicle, customer)) # add vehicle id, makes it easier later

		if float(dead_customers)/config.NEARBY_CUSTOMERS_TO_CHECK > \
			 config.REBUILD_KDTREE_DEAD_CUSTOMERS_THRESHOLD:
			data.rebuild_kdtree()
			return calculate_neighbors_per_vehicle(vehicle)

		return l


	# init neightbors per vehicle
	for i in range(len(routes)):
		neighbors_per_vehicle[i] = calculate_neighbors_per_vehicle(i)

	# pick best one
	route_penalties = 0
	load_penalties = 0

	while data.customers_to_visit:
		candidate = min((i[0] for i in neighbors_per_vehicle))

		_, _, _, _, vehicle, _ = candidate

		# candidate is from vehicle vehicle
		assert neighbors_per_vehicle[vehicle][0] == candidate

		# choose nth elem (randomisation)
		elem = 0
		while rand.random() > 0.4:
			elem += 1
		elem = min(elem, len(neighbors_per_vehicle[vehicle]))
		#print("elem", elem)

		removed = []
		for i in range(elem-1):
			removed.append(heapq.heappop(neighbors_per_vehicle[vehicle]))

		candidate = heapq.heappop(neighbors_per_vehicle[vehicle])

		for rem in removed:
			heapq.heappush(neighbors_per_vehicle[vehicle], rem)


		_, route_dist, route_penalty, load_penalty, vehicle, customer = candidate

		neighbors_per_vehicle[vehicle] = calculate_neighbors_per_vehicle(vehicle)

		#print('choose', candidate)

		# customer might already have been visited by other vehicle, we don't drop these values from other lists
		if customer not in data.customers_visited:
			# use it
			routes[vehicle].append(customer)
			data.customers_to_visit.remove(customer)
			data.customers_visited.add(customer)
			#print('veh', vehicle, ' serves ', customer)

			route_penalties += route_penalty
			load_penalties += load_penalty

			vehicle_loads[vehicle] += customer.demand

			vehicle_route_duration[vehicle] += route_dist
		c2 = min((i[0] for i in neighbors_per_vehicle))
		#print('c2', c2)

	for vehicle, route in enumerate(routes):
		route.append(route[0])

		dist_home = dist(route[-2].pos, route[-1].pos)
		vehicle_route_duration[vehicle] += dist_home

		max_route_duration = route[0].max_route_duration

		if max_route_duration > 0:
			if vehicle_route_duration[vehicle] > max_route_duration:
				overflow = vehicle_route_duration[vehicle] - max_route_duration
				if overflow > dist_home:
					overflow = dist_home # rest has been punished before
				route_penalties += overflow * config.DURATION_EXCEEDED_PENALTY

	from pso import Phenotype # import loop
	return Phenotype(genotype, routes, sum(vehicle_route_duration), route_penalties, load_penalties)


def _get_closest_depots(instance, genotype):
	"""Returns the closest depots for the genotype values. Currently unrandomized."""
	closest_depots=[]

	for vehicle_base in genotype:
		#pprint.pprint(list( ( ( (vehicle_base[0]-d.pos[0])**2 + (vehicle_base[1]-d.pos[1])**2 ), d_id) for (d_id, d) in enumerate(instance.depots) ) )

		# use squared dist
		closest = min( (dist_squared(vehicle_base, d.pos), d_id) for (d_id, d) in enumerate(instance.depots) )

		closest_depots.append( instance.depots[ closest[1] ] )

	return closest_depots



def two_opt(routes, limit):
	"""Do exhaustive 2-opt, return new route"""

	# NOTE: ensure not to introduce a constraint violation.
	# (doesn't change load)
	def do_route(route, limit): # return new route
		if limit == 0:
			return route
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
					return do_route(route_prime, limit-1)

		return route # nothing found

	return list(do_route(route, limit) for route in routes)

