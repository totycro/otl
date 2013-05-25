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

import collections
import random
import math
from pprint import pprint

import tkinter
import tkinter.messagebox

def _loop(root):
	def poll(): # this makes ^C be recognised way faster (somehow!)
		root.after(500, poll)
	root.after(500, poll)
	root.mainloop()
	root.destroy()


def show_instance(instance):
	root, gui = _show_instance(instance)
	_loop(root)


def show_routes(instance, phenotype):
	from pso import Phenotype
	assert isinstance(phenotype, Phenotype)

	routes = phenotype.routes

	root, gui = _show_instance(instance)
	translate_point, inverse_translate_point = get_translate_point(instance)
	for p in phenotype.genotype:
		gui.vehicle_points.append( translate_point(p) )

	_add_routes(instance, routes, gui)

	_loop(root)


def _add_routes(instance, routes, gui):
	translate_point, inverse_translate_point = get_translate_point(instance)
	for route_num, route in enumerate(routes):
		route = route[:]
		route.append(route[0])
		for i in range(len(route)):
			if i == len(route)-1:
				break
			gui.edges.append( (translate_point(route[i].pos), translate_point(route[i+1].pos), route_num) )


	gui.redraw()


def show_genotypes(instance, genotypes, routes=None):
	print(routes)
	root, gui = _show_instance(instance)
	translate_point, inverse_translate_point = get_translate_point(instance)
	#import pdb ; pdb.set_trace()
	gui.genotype_point_sets.extend([[translate_point(p) for p in x] for x in genotypes])
	gui.redraw()

	if routes:
		_add_routes(instance, routes, gui)

	_loop(root)


def get_translate_point(instance):
	sizex = (instance.max_point[0] - instance.min_point[0])
	sizey = (instance.max_point[1] - instance.min_point[1])

	padding_factor = .2
	padding_factor *= .5 # counted twice below

	padding_width = Gui.WIDTH * padding_factor
	padding_height = Gui.HEIGHT * padding_factor

	def translate_point(p):
		nonlocal padding_width, padding_height
		return (((p[0]-instance.min_point[0]) / sizex) * (Gui.WIDTH-2*padding_width) + padding_width,
						((p[1]-instance.min_point[1]) / sizey) * (Gui.HEIGHT-2*padding_height) + padding_height)
	def inverse_translate_point(p):
		nonlocal padding_width, padding_height
		t = ((((p[0] - padding_width)/(Gui.WIDTH-2*padding_width) ) * sizex) + instance.min_point[0],
		     (((p[1] - padding_height)/(Gui.HEIGHT-2*padding_height) ) * sizey) + instance.min_point[1])

		return tuple(int(round(i)) for i in t)
	return translate_point, inverse_translate_point


def _show_instance(instance):
	root = tkinter.Tk()
	gui = Gui(root)

	from instance import Instance
	assert isinstance(instance, Instance)

	translate_point, inverse_translate_point = get_translate_point(instance)
	gui.inverse_translate_point = inverse_translate_point
	gui.set_title(instance.file)

	for c in instance.customers:
		gui.points.append(translate_point(c.pos))

	for d in instance.depots:
		gui.points2.append(translate_point(d.pos))

	gui.redraw()

	return root, gui


class Gui(tkinter.Frame):
	HEIGHT=768
	WIDTH=1024
	def __init__(self, master):
		tkinter.Frame.__init__(self, master)

		self.obj_fun = lambda x : x

		self.master = master

		self.widgets_master = self

		# data
		self.algo = None
		self.points = []
		self.points2 = []
		self.vehicle_points = []
		self.genotype_point_sets = []
		self.edges = []
		self.stepCnt = 0

		# buttons
		btn_start_row = 3
		columns_num = 5

		self.quitBtn = tkinter.Button(self.widgets_master, text="Quit", command=self.on_quit)
		#self.quitBtn.pack({"side": "bottom"})
		self.quitBtn.grid(row=btn_start_row+1, column=2)

		"""
		self.clearBtn = tkinter.Button(self.widgets_master, text="Restart", command=self.on_restart)
		#self.clearBtn.pack({"side": "bottom"})
		self.clearBtn.grid(row=btn_start_row, column=1)

		self.stepBtn = tkinter.Button(self.widgets_master, text="Step", command=self.on_step)
		#self.stepBtn.pack({"side": "bottom"})
		self.stepBtn.grid(row=btn_start_row, column=2)

		self.nextPointBtn = tkinter.Button(self.widgets_master, text="Add point", command=self.on_next_point)
		self.nextPointBtn.grid(row=btn_start_row, column=3)

		self.finishBtn = tkinter.Button(self.widgets_master, text="Finish", command=self.on_finish)
		self.finishBtn.grid(row=btn_start_row+1, column=3)

		self.randomBtn = tkinter.Button(self.widgets_master, text="Random", command=self.on_random)
		self.randomBtn.grid(row=btn_start_row+1, column=2)
		"""

		self.label = tkinter.Label(self.widgets_master, text="")
		self.label.grid(row=1, column=0, columnspan=columns_num)

		self.label2 = tkinter.Label(self.widgets_master, text="")
		self.label2.grid(row=5, column=0, columnspan=columns_num)

		# canvas
		self.canvas = tkinter.Canvas(self.widgets_master, width=self.WIDTH, height=self.HEIGHT, bg='white')
		self.canvas.grid(row=0, columnspan=columns_num)

		self.canvas.bind("<ButtonPress-1>", self.on_click)
		self.canvas.bind("<Motion>", self.on_motion)

		def q(*args, **kwargs):
			self.on_quit()
		self.bind_all("<Control-q>", q)

		self.set_title()
		self.pack()

		"""
		MyEvent = collections.namedtuple("MyEvent", ["x", "y"])
		self.on_click( MyEvent(200, 100) )
		self.on_click( MyEvent(120, 140) )
		self.on_click( MyEvent(130, 180) )
		self.on_click( MyEvent(250, 200) )
		self.on_click( MyEvent(230, 150) )
		self.on_click( MyEvent(300, 160) )
		self.on_click( MyEvent(170, 200) )
		"""

		#self.points = [(170, 200), (348, 220), (387, 108), (246, 186), (269, 211), (246, 197), (265, 260), (230, 150), (261, 220), (200, 100), (309, 249), (312, 61), (304, 196), (411, 157), (130, 180), (538, 197), (311, 154), (269, 95), (288, 87), (300, 148), (335, 146), (394, 209), (305, 192), (178, 206), (250, 200), (249, 251), (120, 140), (206, 227), (263, 203), (450, 261), (330, 118), (371, 299), (356, 171), (245, 83), (157, 241), (273, 167), (300, 160), (259, 223), (273, 163), (170, 129), (311, 129), (326, 241)]
		#self.points = [(356, 252), (339, 218), (429, 239), (290, 308), (263, 179), (345, 180), (339, 192), (180, 338), (296, 250), (200, 100), (431, 155), (406, 217), (374, 205), (358, 335), (372, 287), (322, 222), (343, 322), (321, 264), (398, 213), (271, 243), (233, 89), (400, 172), (346, 303), (227, 239), (211, 231), (236, 300), (331, 246), (340, 224), (252, 149), (377, 130), (324, 254), (209, 338), (242, 256), (386, 230), (377, 177), (229, 75), (144, 228), (388, 273), (397, 199), (408, 226), (286, 135), (432, 337), (284, 157), (295, 198), (269, 145), (347, 234), (301, 221), (219, 318), (335, 173), (208, 290), (281, 174), (422, 165), (292, 248), (229, 200), (266, 260), (311, 348), (275, 196), (120, 140), (356, 188), (283, 150), (384, 187), (300, 219), (253, 275), (171, 168), (402, 142), (368, 156), (269, 166), (306, 176), (328, 262), (392, 260), (170, 200), (311, 191), (333, 163), (228, 110), (325, 211), (409, 160), (230, 150), (318, 211), (480, 157), (247, 210), (347, 247), (349, 231), (97, 275), (208, 181), (289, 262), (294, 367), (514, 160), (233, 283), (298, 336), (301, 108), (244, 267), (250, 200), (238, 224), (254, 69), (293, 183), (377, 214), (252, 146), (367, 214), (300, 160), (404, 213), (342, 204), (294, 225), (387, 254), (398, 219), (235, 257), (136, 146), (232, 304), (316, 339), (227, 226), (341, 239), (360, 181), (209, 212), (402, 154), (146, 253), (370, 230), (328, 189), (260, 263), (446, 211), (331, 145), (330, 107), (257, 332), (224, 153), (130, 180), (284, 104), (327, 74), (345, 214), (296, 218), (284, 159), (193, 236), (440, 161), (256, 160), (203, 180), (247, 269), (366, 219), (290, 221), (422, 127), (224, 197), (274, 146), (416, 105), (253, 165)]


		self.redraw()

	def on_quit(self):
		self.quit()

	def on_step(self):
		pass

		self.redraw()

	def on_next_point(self):
		self.on_step()

	def on_finish(self):
		return

	def on_click(self, event):
		print('click')

		if self.algo: # algo running
			ans = tkinter.messagebox.askyesno("New run?", "You can't add points while the algorithm is running.\nRestart it?")
			if not ans:
				return

			self.algo = None

		self.points.append((event.x, event.y))
		print('new point', self.points[-1])
		self.redraw()

	def on_random(self):
		MyEvent = collections.namedtuple("MyEvent", ["x", "y"])
		spacing = 10
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()

		#points_num = random.randint(8, 10)
		points_num = 30
		#points_num = 60
		#points_num = 120

		for i in range(points_num):
			x = random.gauss(width/2, width/7)
			y = random.gauss(height/2, height/7)

			x = int(x)
			y = int(y)

			self.on_click( MyEvent(x, y) )

	def redraw(self):
		self.clear()
		self.draw()

	def clear(self):
		self.canvas.delete("all")

	def draw(self):
		if self.algo:
			self.algo.draw(self.canvas)
		for p in self.points:
			sz = 4
			self.canvas.create_oval( p[0]-sz, p[1]-sz, p[0]+sz, p[1]+sz, fill="red")
		for p in self.points2:
			sz = 4
			self.canvas.create_oval( p[0]-sz, p[1]-sz, p[0]+sz, p[1]+sz, fill="black")

		for i, p in enumerate(self.vehicle_points):
			sz = 4
			self.canvas.create_oval( p[0]-sz, p[1]-sz, p[0]+sz, p[1]+sz, fill=self.get_color(i))

		for i, p_set in enumerate(self.genotype_point_sets):
			sz = 4
			for p in p_set:
				self.canvas.create_oval( p[0]-sz, p[1]-sz, p[0]+sz, p[1]+sz, fill=self.get_color(i))

		for edge in self.edges:
			self.canvas.create_line(edge[0][0], edge[0][1], edge[1][0], edge[1][1], fill=self.get_color(edge[2]), width=3.0)

	def get_color(self, i):
		colors = "blue", "green", "brown", "pink", "yellow", "black", "cyan", "maroon", "olive", "lime", "fuchsia", "silver", "magenta", "grey", "navy", "teal", "aqua"
		return colors[i%len(colors)]

	def on_restart(self):
		ans = tkinter.messagebox.askyesno("Clear points?", "Clear points as well?")
		if ans:
			self.points = []
		self.algo = None
		self.redraw()

	def on_motion(self, event):
		s = str((event.x, event.y))
		if hasattr(self, "inverse_translate_point"):
			s+= " " + str(self.inverse_translate_point( (event.x, event.y) ) )

		self.label2.config(text=s)

	def set_title(self, title=""):
		to_add = ""
		if title:
			to_add = ": "+title
		self.label.config(text="Presentation of pso-mdvrp"+to_add)