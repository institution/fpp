import sys
from parse_svg import accept_mm, accept_path, accept_viewBox, make_path
from path import distance, Vec, Bezier1, project, Poly, Line
from path import intersect_poly_poly, intersect_poly_line, flattern_bezier_list
import xml.etree.ElementTree as ET
from log import fail, info, warning
from reader import Reader
import math



TOLERANCE_MM = 0.02
STEP_MM = 0.5

SHOW_GUI = 0
PRINT_OUTPUT = 0


if SHOW_GUI:
	import matplotlib.pyplot as plt

"""
Note on units: every variable stores value in [u] (unless postfix _mm), use mm_to and to_mm for input, output
"""

"""
# TODO: add scale 1cm x 1cm box to output ?
# TODO: print ruler with values to output ?
# TODO: thinner line in output <- set to mm ?


# TODO: add cover start indicator

# TODO: Alert on negative values on the profil -- check h value in calc_value

# TODO: think of some sanity check on output? -> 
            check last point == first point   if applicable
            rectangular test case

"""


#width="{width}"
#height="{height}"
OUTPUT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"   
   
   viewBox="{viewbox}"   
   id="svg2"
   version="1.1">
  <defs
     id="defs4" />
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>  
  <path
     id="sciana"
     d="{path}"
     style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;image-rendering:auto" />
</svg>
"""


def get_aabb(ps):
	min_x = +2**30
	min_y = +2**30
	max_x = -2**30
	max_y = -2**30
	
	for x,y in ps:
		if x > max_x:
			max_x = x
		if x < min_x:
			min_x = x
			
		if y > max_y:
			max_y = y
		if y < min_y:
			min_y = y
			
	return Vec(min_x,min_y),Vec(max_x,max_y)
	

def save_cover_svg(ps, oname, to_mm):
	assert len(ps) > 0
		
	a,b = get_aabb(ps)
	
	d = b - a
			
	vb = (a[0],a[1],d[0],d[1])
		
	
	
	path =  "M {:.6f},{:.6f} ".format(*ps[0]) + " ".join("{:.6f},{:.6f}".format(*p) for p in ps[1:])
	
	with open(oname, 'wb') as f:
		f.write(
			OUTPUT_TEMPLATE.format(
				path = path,
				width="{:.6f}mm".format(d[0]*to_mm),
				height="{:.6f}mm".format(d[1]*to_mm),
				viewbox="{:.6f} {:.6f} {:.6f} {:.6f}".format(*vb)
			).encode('utf-8')
		)
		
	info("written to {}".format(oname))


def save_output_svg(ps, oname, to_mm):
	
	assert len(ps) > 0
	
	max_y = 0
	for x,y in ps:
		if y > max_y:
			max_y = y
	
	max_x = ps[-1][0]
	min_x = ps[ 0][0]
	
	w = max_x - min_x
	h = max_y
				
	vb = (min_x,0,w,h)
	
	
	
	ps.append((max_x,0))
	ps.append((min_x,0))
	
	path = "M {:.6f},{:.6f} ".format(min_x,0) + " ".join("{:.6f},{:.6f}".format(*p) for p in ps)
	
	with open(oname, 'wb') as f:
		f.write(
			OUTPUT_TEMPLATE.format(
				path = path,
				width="{:.6f}mm".format(w*to_mm),
				height="{:.6f}mm".format(h*to_mm),
				viewbox="{:.6f} {:.6f} {:.6f} {:.6f}".format(*vb)
			).encode('utf-8')
		)

	info("written to {}".format(oname))
	







def get_conversion_mm(vb, w_mm, h_mm):
	"""
	return -- to_mm, mm_to
	"""
	x0,y0,dx,dy = vb
	
	to_mmx = w_mm/dx
	to_mmy = h_mm/dy
	assert math.isclose(to_mmx, to_mmy), (to_mmx, to_mmy)
	
	to_mm = to_mmx
	mm_to = dx/w_mm
	return to_mm, mm_to
	
	

	
def read_poly_from_svg_path(root, name, tolerance):
	x = root.find(".//*[@id='"+name+"']")
	if x != None:
		beziers = make_path(accept_path(Reader(x.get('d'))))
		err, vertices = flattern_bezier_list(beziers, tolerance)		
		return Poly(vertices)
		
	else:		
		return None









def show(point_obrys, point_profil, value_mm):
	vis1, = Bezier1(point_obrys, point_profil).render(plt)		
	vis2 = plt.text(
		x=point_profil[0] + 15, 
		y=point_profil[1], 
		s="{:.1f}mm".format(value_mm),
		verticalalignment='center',
		backgroundcolor='white',
		#bbox=dict(facecolor='white', alpha=0.8),
		#size=12
	)
	
	plt.show()
	plt.pause(0.001)
	#plt.waitforbuttonpress(timeout=-1)
	
	vis1.remove()
	vis2.remove()




def calc_value(pos, obrys, profil, odcinek, to_mm):
	##TODO: Calculate sidewall and cover point
	##TODO: (height, dist) -- sidewall height, distance along obrys from start point
	
	
	odcinek_dir = odcinek.get_dir()
	ort_odcinek = Vec(odcinek_dir[1], -odcinek_dir[0])
	
	
	point_obrys = obrys.get_point(pos)
	
	point_odcinek, _ = project(point = point_obrys, line = odcinek)
	
	orto_line = Line(point_odcinek, point_odcinek + ort_odcinek)
	orto_unit = orto_line.get_length()
	
	cover_x,cover_y = None, None
	
	
	ths = intersect_poly_line(poly = profil, line = orto_line)
	if len(ths) == 1:
		t,h = ths[0]
		point_profil = profil.get_point(t)

		# assert all hs are having the same sign
		h
		
		cover_x = t
		
	else:
		fail('ERROR: unique intersection point of profil and orto_line is undefined')
		
	
	_, cover_h = project(point = point_obrys, line = orto_line)
	
			
	value = distance(point_odcinek, point_profil)
	
	if SHOW_GUI:
		show(point_obrys, point_profil, value * to_mm)
	
	return value, Vec(cover_x, cover_h * orto_unit)



import os.path

def main():
	
	if len(sys.argv) != 2:
		print("Usage: fpp <input.svg>")
		sys.exit(0)
	
	iname = sys.argv[1]
	name = os.path.splitext(iname)[0]
	
	info("opening: {!r}".format(iname))
	
	tree = ET.parse(iname)
	root = tree.getroot()
	
	vb = accept_viewBox(Reader(root.get('viewBox')))
	w_mm = accept_mm(Reader(root.get('width')))
	h_mm = accept_mm(Reader(root.get('height')))
	to_mm, mm_to = get_conversion_mm(vb, w_mm, h_mm)
		
	info("width : {:.1f}mm".format(w_mm))
	info("height: {:.1f}mm".format(h_mm))
	
	#info("scale: 1mm is {:.3f}".format(1*mm_to))
	#info("scale: 1 is {:.3f}mm".format(1*to_mm))
	
	tolerance = TOLERANCE_MM * mm_to
	
	profil = read_poly_from_svg_path(root, 'profil', tolerance)
	if profil == None:		
		fail("ERROR: brak profilu na rysunku")
	
	obrys = read_poly_from_svg_path(root, 'obrys', tolerance)
	if obrys == None:
		fail("ERROR: brak obrysu na rysunku")
		
	
	
	
	info("obrys : length {:.1f}mm divided into {} segments".format(obrys.get_length()*to_mm, obrys.size()))
	info("profil: length {:.1f}mm divided into {} segments".format(profil.get_length()*to_mm, profil.size()))
	
	
	info("tolerance: {}mm".format(TOLERANCE_MM))
	info("step size: {}mm".format(STEP_MM))
	
	
	pos = 0.0
	
	
	cross_poczatek = read_poly_from_svg_path(root, 'start', tolerance)
	if cross_poczatek != None:
		info("setting start point")
		ths = intersect_poly_poly(obrys, cross_poczatek)
		if len(ths) != 1:
			fail("ERROR: poczatek nie przecina obrysu w dokladnie 1 punkcie")
		else:		
			t,_ = ths[0]
			pos = t
	else:
		info("start point not found")
	
	end = pos
			
	cross_koniec = read_poly_from_svg_path(root, 'end', tolerance)
	if cross_koniec != None:
		info("setting end point")
		ths = intersect_poly_poly(obrys, cross_koniec)
		if len(ths) != 1:
			warning("WARNING: koniec nie przecina obrysu w dokladnie 1 punkcie")
		else:
			t,_ = ths[0]
			end = t
	else:
		info("end point not found")
	

	if pos < end:
		delta = end - pos
	else:
		delta = obrys.get_length() - (pos - end)
		
	assert delta > 0
	assert delta <= obrys.get_length()
		
	odcinek = Line(
		profil.get_point(0),
		profil.get_point(profil.get_length()),
	)
	

	
	
	# setup view
	if SHOW_GUI:
		plt.ion()
		plt.show()
		plt.axis([vb[0], vb[0]+vb[2], vb[1], vb[1]+vb[3]])
				
		profil.render(plt)
		obrys.render(plt)
		odcinek.render(plt)
		if cross_poczatek:
			cross_poczatek.render(plt)
		if cross_koniec:
			cross_koniec.render(plt)
			

	rs = []
	rs_cover = []
	
	
	info("running now...")
	
	last_progress = 0
	
	step = STEP_MM * mm_to
	total = 0.0
	
	while total < delta:
	
		# print("pos,end = {:.1f},{:.1f}".format(pos*to_mm,end*to_mm))
		# print("total,delta = {:.1f},{:.1f}".format(total*to_mm,delta*to_mm))
				
		value, cover_p = calc_value(pos, obrys, profil, odcinek, to_mm)	
		if PRINT_OUTPUT:	
			print("OUTPUT: {:6.1f} {:6.1f} [mm] {:6.1f} {:6.1f} [u]".format(total*to_mm, value*to_mm, pos, value))
		
		progress = int((total/delta) * 100)
		if progress % 20 == 0 and progress != last_progress:
			info("{:5}% done...".format(progress))
			last_progress = progress
		
		
		rs.append( (total, value) )
		rs_cover.append( cover_p )
		
		
		
		
		pos += step
		
		if pos > obrys.get_length():
			pos -= obrys.get_length()
		
		total += step
		
	# value at the end
	total = delta
	pos = end
	value, cover_p = calc_value(pos, obrys, profil, odcinek, to_mm)
	if PRINT_OUTPUT:
		print("OUTPUT: {:6.1f} {:6.1f} [mm] {:6.1f} {:6.1f} [u]".format(total*to_mm, value*to_mm, pos, value))
		
	rs.append((total, value))
	rs_cover.append( cover_p )
	
	info("{} points generated".format(len(rs)))
			
		
	save_output_svg(rs, "{}-sidewall.svg".format(name), to_mm)
	save_cover_svg(rs_cover, "{}-cover.svg".format(name), to_mm)

	
if __name__ == '__main__':
	main()
