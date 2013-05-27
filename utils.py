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


dist_squared = lambda x, y: (x[0]-y[0])**2 + (x[1]-y[1])**2
dist = lambda x, y: ((x[0]-y[0])**2 + (x[1]-y[1])**2) ** 0.5

def pprint_list_of_list_of_floats(l):
	print("[", end="\n");
	for i, l1 in enumerate(l):
		# l1 is list of tuples/list of sz 2
		print("%s: ["%i, end="");

		for t in l1:
			#print("now:")
			#pprint(t)
			print("(%04.1f, %04.1f), " % (float(t[0]), float(t[1])), end="");

		print("]", end="")
		print(",", end="\n");

	print("]")



def pprint_list_of_floats(l1):
		# l1 is list of tuples/list of sz 2
		print("[", end="");

		for t in l1:
			#print("now:")
			#pprint(t)
			print("(%05.1f, %05.1f), " % (float(t[0]), float(t[1])), end="");

		print("]", end="")
		print(",", end="\n");


#def print_avg_velocity(velocities)