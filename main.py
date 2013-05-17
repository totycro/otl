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

from instance import Instance
from gui import show_instance


if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("You need to specify an instance file.");
		sys.exit(1)

	inputfile = sys.argv[1]

	instance = Instance(inputfile)

	#show_instance(instance)