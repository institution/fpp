import sys
from parse_svg import read_svg
from path import distance, Vec, Bezier1, intersect, project, Path


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

class Output:
	def __init__(self):
		self.ps = []
	
	def write(self,x,y):
		self.ps.append((x,y))
		
	def save(self, to_mm):
		
		max_y = 0
		max_x = 0
		for x,y in self.ps:
			if x > max_x:
				max_x = x
			if y > max_y:
				max_y = y
				
		vb = (0,0,max_x,max_y)
		
		w = max_x
		h = max_y
		
		self.ps.append((max_x,0))
		
		path = "M 0,0 " + " ".join("{:.6f},{:.6f}".format(*p) for p in self.ps)
		
		with open("output.svg", 'wb') as f:
			f.write(
				OUTPUT_TEMPLATE.format(
					path = path,
					width="{:.6f}mm".format(w*to_mm),
					height="{:.6f}mm".format(h*to_mm),
					viewbox="{:.6f} {:.6f} {:.6f} {:.6f}".format(*vb)
				).encode('utf-8')
			)
		

def main():
	"""
	Note on units: every variable stores value in [u], use mm_to and to_mm for input, output
	"""
	
	# TODO: Alert on negative values on the wall
	

	import matplotlib.pyplot as plt
	plt.ion()
	plt.show()

	out = Output()

	obrys,profil,to_mm,mm_to,box = read_svg(sys.argv[1])

	plt.axis([box[0], box[2], box[1], box[3]])
	
	

	# TODO assert max section length
	profil = profil.flattern()
	obrys = obrys.flattern()

	k0 = profil.get_point(0)
	k1 = profil.get_point(profil.get_length())
	odcinek = Bezier1(k0,k1)

	d = odcinek.get_dir()
	od = Vec(d[1], -d[0])
		
	profil.render(plt)
	obrys.render(plt)
	odcinek.render(plt)

	vis1 = None
	vis2 = None
	
	pos = 0*mm_to
	while pos < obrys.get_length():
		point_obrys = obrys.get_point(pos)
		
		point_odcinek = project(point=point_obrys, line=odcinek)
		
		orto_line = Bezier1(point_odcinek, point_odcinek + od)
		
		point_profil = intersect(line = orto_line, path = profil)
		
		#point1
		
		value = distance(point_odcinek, point_profil)
		print("OUTPUT: {:6.1f} {:6.1f} [mm] {:6.1f} {:6.1f} [u]".format(pos*to_mm, value*to_mm, pos, value))
		out.write(pos, value)
		
		vis1, = Bezier1(point_obrys, point_profil).render(plt)
		
		vis2 = plt.text(
			x=point_profil[0] + 15, 
			y=point_profil[1], 
			s="{:.1f}mm".format(value*to_mm),
			verticalalignment='center',
			backgroundcolor='white',
			#bbox=dict(facecolor='white', alpha=0.8),
			#size=12
		)
		
		plt.show()
		plt.pause(0.01)
		vis1.remove()
		vis2.remove()
		
		pos += 10*mm_to
		
	out.save(to_mm)
	
	
if __name__ == '__main__':
	main()
