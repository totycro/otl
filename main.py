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

	if '-a' in sys.argv:
		iterations = 80
		outfile = open("test.out", "a")
		outfile.write("Running tests (seed: %s, it: %d)\n" % (seed, iterations) )
		outfile.write("Config: %s\n" % (Config.__dict__) )
		outfile.flush()
		#for inst in ("instances/p0%d" % d for d in ( 1, 2, 3, 4, 5 )):
		for inst in ("instances/p0%d" % d for d in range(10)):
			#outfile.write("cur rand state: %s"% str(rand.getstate()))
			check_instance(outfile, inst, rand, iterations)
		for inst in ("instances/p%d" % d for d in range(10, 24)):
			check_instance(outfile, inst, rand, iterations)
		sys.exit(0)

	inputfile = sys.argv[1]

	instance = Instance(inputfile)

	#rand.setstate(rand_state_err)
	pso(instance, rand, Config(iterations=iterations))

	#rand_state_err = (3, (2213444479, 4282063371, 2760720211, 4257548846, 2384261257, 1682005459, 1731041884, 1008981499, 354316193, 691426136, 4223991522, 3441724649, 3721811652, 1416682745, 434055191, 3854775491, 3472531633, 4175468582, 213251410, 2273736482, 1414122564, 1055026350, 2448397431, 1894388712, 3213802032, 3877387184, 3440013383, 4294195428, 1895279303, 1913620995, 867826987, 1850813734, 1270355017, 2167080594, 2530961400, 1883803162, 2121045585, 3255462819, 1484689222, 1077051676, 3888348871, 2990007039, 229567971, 2230758806, 1434415908, 4184864447, 1384047070, 760250431, 830352498, 1561218251, 1653946783, 1132670085, 2509687561, 859184656, 1830806398, 3428425258, 302893656, 661214474, 2960501396, 3253342427, 788574506, 4058443835, 1780633683, 2378413727, 164861702, 197038218, 2179273497, 1370400424, 3402338143, 2614670119, 2026705100, 1315863034, 1295546293, 1209465651, 3647415, 3368565772, 3460431327, 222393928, 2320618959, 355447257, 1164397747, 542270941, 3323841264, 2337558699, 1581538587, 4031270469, 399534688, 3175330493, 644144384, 2084213074, 3393337974, 2581880295, 2833235352, 2437942974, 2247114308, 3579145376, 1026692467, 1652369491, 134374570, 407252633, 3842849749, 3253948510, 2614000630, 663572371, 3333617112, 1944810651, 1838806190, 3098703728, 3306524497, 3952048300, 4144543162, 343453271, 2441422872, 2986705506, 539862545, 4282427828, 94417572, 1832617200, 3195619388, 3889959257, 607326807, 514465117, 903491946, 3963241828, 1971448557, 132435645, 2405888995, 754755609, 400476453, 2520188680, 3098579727, 3608015173, 2930458274, 4095259934, 930017730, 3662937193, 2950371347, 1987324665, 2613020834, 897370704, 30513366, 982708358, 1772104179, 937915940, 1347989976, 1070840535, 3171097015, 2664758501, 2821087176, 3243360409, 1658785379, 1987929599, 1431316600, 1897652542, 825855335, 2001001069, 1285372083, 3185161695, 276517630, 2375622823, 3152661237, 585273248, 418047018, 3349103333, 2333806369, 982258851, 1869163463, 333753194, 2920290353, 791364687, 2452380629, 2163155436, 3133828404, 1962055842, 1030556921, 2418397412, 2202953979, 626482141, 858215475, 2573794786, 508864366, 2809404996, 2170554902, 4222622025, 3915816311, 4019243271, 1233721228, 433861025, 1611532460, 3367257556, 3372190429, 1314762323, 3289410650, 2040919131, 2969988883, 3462141996, 485507255, 990626092, 4145279223, 1160330767, 3642220264, 3228575876, 678036448, 1834446973, 1986261117, 401396505, 3644840065, 2142623695, 3371566143, 3734238100, 3656759665, 145579774, 2156289089, 4266648117, 4156152436, 3957500180, 710336954, 1303788703, 1869271820, 2664195188, 103909085, 3016259861, 918227550, 1417799250, 2262494537, 1124572767, 131708547, 2380527405, 1016502399, 2315241858, 1922346529, 731168272, 2885871719, 1920472838, 2727922142, 627172549, 4279894347, 643030143, 3033110667, 2995615383, 1573712975, 3360711095, 3800738927, 4166221588, 1979026584, 858470515, 2539253051, 1775136815, 1586054881, 3779745162, 1080658443, 664910563, 3842818298, 1656763680, 2975566236, 2572722991, 2655399567, 3032814032, 2739576197, 137601612, 4012830660, 2580933134, 1245585529, 1309794779, 2927140734, 1542889981, 1881173530, 2563999969, 3187920934, 941462473, 1588888595, 3942797979, 1331966835, 2359558859, 472602604, 935156745, 2238673706, 1600728279, 3480609143, 2628040904, 2045729422, 660475191, 1334755061, 479219360, 1480338659, 386953344, 2942606945, 1700209599, 1449787140, 2881304267, 2029510924, 3962807842, 4159104649, 810067765, 2068672399, 2479959982, 1918752975, 3766750143, 2246459673, 1898061519, 2387765122, 3414497844, 626195355, 2964019282, 1025601053, 2286405883, 391231263, 3734338933, 1706641966, 2472905391, 515948112, 351685863, 3415768289, 3428664770, 2226836694, 2864744580, 2590934150, 3122752217, 1348839379, 1470345088, 1583756900, 2069098329, 1411727415, 245593502, 2188777062, 2105718580, 1163852337, 1801317776, 1465834438, 3901486030, 2607841546, 1083607394, 2405779573, 2865277240, 1368281860, 3168161470, 1355953290, 660911701, 1058468054, 1987099999, 2337966772, 2555371903, 3371311446, 2827360292, 1779029579, 2105778535, 3350537775, 1419139371, 2545119930, 689814352, 1180446227, 1090877079, 806665010, 3727237168, 1448496505, 4229075049, 1299730896, 1493302846, 2669973507, 3136039236, 983014657, 262471850, 1649653619, 1110290555, 2494216193, 2653532274, 2742159609, 1263493298, 3059465811, 3249920815, 152540143, 1393690472, 934404553, 2145633899, 3477530733, 1984843532, 2083966749, 1651908135, 301713574, 4066817409, 3470530474, 2735000441, 922048791, 1356358711, 3594579137, 4239508522, 2738860120, 920381682, 1833885112, 3055192079, 704498264, 2879674226, 426599798, 4186131946, 532485005, 3651282282, 2886556463, 1155230017, 1663062441, 2986232064, 8228846, 137644171, 124533191, 4097206094, 3167412324, 2152400417, 4236824874, 2042803822, 113373700, 2505086387, 767519089, 2200321449, 3311590078, 83768015, 2202261678, 3829466114, 4209187867, 356873402, 3340306263, 1782308974, 1099601174, 1754793974, 2324709590, 2260238670, 1580395883, 1014997596, 2003254649, 723369550, 1918374322, 1060742884, 827219728, 1971416161, 1553333422, 3501144842, 3831919002, 2857464085, 3768866350, 2350660582, 966284204, 3326985457, 3459394383, 1988301144, 3753986948, 4266313377, 573852665, 3748069610, 3255705543, 459457825, 155081032, 3292213289, 3845632404, 507711698, 3225754755, 992908870, 1625452734, 2735425563, 1998207503, 3261137794, 3414023364, 2667074083, 2199759593, 3344843442, 2702675945, 206467413, 2581506499, 3241403047, 3947306264, 1517333009, 3953908853, 1588414201, 527064025, 959757712, 1702561230, 701165604, 869993100, 2114437630, 150341829, 2861373356, 949001175, 2265231096, 473516778, 1151262194, 1750479702, 3827114667, 2583729214, 3374256876, 899987574, 2507450208, 1497303726, 4286149784, 3487998075, 920516964, 3469184442, 3048448069, 3752294524, 395457502, 4037618292, 896285665, 3227421808, 4279480574, 2183002038, 1609173608, 1156220108, 162570903, 3340506758, 3188219120, 983387818, 1575537144, 444393592, 2077076122, 996229948, 1585747720, 2671075587, 1297231553, 1456610595, 996500774, 1952556931, 4134105, 3694414909, 2042092800, 658156786, 3108363252, 4121677719, 3646860887, 1060104510, 2342052905, 286124440, 473699483, 2346509879, 3352904013, 3786667572, 2401586099, 2319911365, 147141749, 499223501, 1302128197, 1045671423, 327046392, 1889925728, 2982649422, 20404679, 1453785606, 534566878, 1204591466, 3684727205, 4054776201, 2739666295, 1757804948, 1391230084, 1596824227, 1160882263, 556492191, 3739139163, 2937162478, 1455369308, 1596426638, 265715834, 2142365903, 1209411781, 1342955189, 724717504, 2394352961, 1766941769, 3266569280, 2332092469, 3476637734, 4162509190, 1616154764, 1766948402, 161532505, 2337931529, 1941647638, 858044123, 2005861774, 2524642281, 4090422130, 1833736392, 872656393, 2282434806, 4081863448, 557740255, 2697882565, 3905818701, 196862839, 2763432030, 1772829633, 513322633, 3307152073, 1135596782, 299518345, 3324187248, 2363916981, 3131566849, 2425183727, 4189165985, 3809394142, 3212708348, 3825305561, 2311081640, 740570105, 1276180943, 1230145194, 1011562680, 4251950530, 3009973192, 121429728, 1746553715, 2048031942, 2716984870, 1254020494, 1599082386, 2704383275, 666125577, 1420802577, 3905414600, 1066473900, 2650652923, 3111079382, 1240258162, 3911053563, 3043370019, 3324115268, 868939936, 1962071631, 242), None)



	#show_instance(instance)


