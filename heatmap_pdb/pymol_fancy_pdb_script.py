
bg_color white
set orthoscopic, on
set antialias, 2


hide everything
show cartoon
set cartoon_ring_mode, 3
set cartoon_nucleic_acid_mode, 4
set cartoon_ladder_mode, 0
set cartoon_ring_transparency, 0.2


spectrum b, blue_white_red



show spheres, (resid 24)
color gray40, (resid 24)
show spheres, (resid 25)
color gray40, (resid 25)
set sphere_scale, 0.6



dist hbonds, (resn DG+G+DC+C and name N7+O6+N2+N1), (resn DG+G+DC+C and name N7+O6+N2+N1), 3.3
hide labels, hbonds
set dash_color, black
set dash_gap, 0.3
set dash_width, 2


set ray_trace_mode, 1
set ambient, 0.5
set reflect, 0.2
set shininess, 50
set spec_reflect, 0.1


orient
ray 1200, 1200
