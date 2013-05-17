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


from collections import namedtuple


class Instance:

	def __init__(self, file):
		self.file = file

		f = open(file, "r")

		line_iter = iter(f.read().splitlines())

		get_next_line_data = lambda : [i for i in next(line_iter).split(" ") if i]

		head = get_next_line_data()

		if int(head[0]) != 2:
			raise Exception("Not a MDVRP input file")

		self.num_vehicles = int(head[1])
		self.num_customers = int(head[2])
		self.num_depots = int(head[3])

		print(self)

		self.depots= []
		depot_type = namedtuple("Depot", ["pos", "max_route_duration", "max_vehicle_load"])

		for d in range(self.num_depots):
			line = get_next_line_data()
			# line is D Q
			self.depots.append( {"pos": None, "max_route_duration": int(line[0]), "max_vehicle_load": int(line[1])} )

		customer_type = namedtuple("Customer", ["pos", "service_duration", "demand" ])

		self.customers = []

		for c in range(self.num_customers):
			line = get_next_line_data()
			# line is i x y d q f a list e l
			self.customers.append( customer_type(pos=(int(line[1]), int(line[2])),
			                                     service_duration=int(line[3]),
			                                     demand=int(line[4])) )

		for d in range(self.num_depots):
			line = get_next_line_data()
			# line is i x y d q f a list e l, but for depot
			data = self.depots[d]
			data["pos"] = ( int(line[1]), int(line[2]) )
			self.depots[d] = depot_type(**data)

		try:
			next(line_iter)
		except StopIteration:
			# that's what we're going for
			pass
		else:
			raise Exception("Garbage at end of file")







	def __str__(self):
		s = ""
		s += "Instance\t%s\n" % self.file
		s += "Vehicles\t%s\n" % self.num_vehicles
		s += "Customers\t%s\n" % self.num_customers
		s += "Depots\t\t%s" % self.num_depots
		return s



