from reader import Reader
from path import Path, Bezier1, Bezier3, Vec
import sys, math

def fail(msg):
	print(msg)
	sys.exit(-1)
	
def warning(msg):
	print("WARNING: "+msg)
	
def info(msg):
	print("INFO: "+msg)
	

FLOAT = "+-0.123456789"
CMDS = "mzlcMZCL"
COMMA = ','
WHITE = " \t\n"

def accept_white(r):
	i = 0
	while r.peek() in WHITE:
		r.get()
		i += 1
	return i

def accept_char(r, c):
	if r.peek() == c:
		r.get()
		accept_white(r)
		return c
	else:
		fail("ERROR: parser: expected: {!r}".format(c))
		
	
def accept_point(r):
	x = accept_number(r)
	accept_char(r, ',')
	y = accept_number(r)
	return Vec(x,y)

def accept_path(r):
	
	elems = []
	
	accept_white(r)
	while 1:
		if r.peek() in CMDS:
			elems.append(r.get())
			accept_white(r)
			
		elif r.peek() in FLOAT:
			elems.append(accept_point(r))
						
		elif r.peek() == 'TERMINAL':
			break
		
		else:
			fail("ERROR: parser: unexpected symbol: {!r}".format(r.peek()))
			
	return elems
			
			
def accept_mm(r):
	x = accept_number(r)
	accept_char(r, 'm')
	accept_char(r, 'm')
	return x
			
def accept_viewBox(r):
	x0 = accept_number(r)
	y0 = accept_number(r)
	x1 = accept_number(r)
	y1 = accept_number(r)
	return x0,y0,x1,y1

def accept_number(r):
	xs = []
	if r.peek() not in FLOAT:
		fail("ERROR: expected float: found: {!r}".format(r.peek()))
	
	while r.peek() in FLOAT:
		xs.append(r.get())
	
	accept_white(r)
	
	s = ''.join(xs)
	try:
		return float(s)
	except ValueError:
		fail("ERROR: parser: cannot convert symbol to float: {!r}".format(s))
		
			

def get_arity(c):
	return {
		'm': 1,	
		'z': 0,
		'l': 1,
		'c': 3,		
		'M': 1,	
		'Z': 0,
		'L': 1,
		'C': 3,	
	}[c]

def make_path(prog):
	parts = []
	cmd = '?'	       # current command
	args = [Vec(0,0)]  # current args
			
	i = 0
	while i < len(prog):
	
		# read new command if any
		if isinstance(prog[i], str):
			cmd = prog[i]
			i += 1

		# read args
		j = i + get_arity(cmd)
		while i < j:
			args.append(prog[i])
			i += 1
		
		
		if cmd == 'm':			
			d = args.pop()
			cp = args.pop()
			np = cp + d
			cmd = 'l'		
			args.append(np)
			
		elif cmd == 'M':
			np = args.pop()
			cp = args.pop()
			cmd = 'L'
			args.append(np)	
			
		elif cmd == 'z' or cmd == 'Z':
			cp = args.pop()
			np = parts[0].get_point(0.0)
			parts.append(Bezier1(cp, np));
			cmd = '?'
			args.append(np)
			
		elif cmd == 'l':
			d = args.pop()
			cp = args.pop()
			np = cp + d
			parts.append(Bezier1(cp, np));
			cmd = 'l'
			args.append(np)

		elif cmd == 'L':
			np = args.pop()
			cp = args.pop()
			parts.append(Bezier1(cp, np));
			cmd = 'L'
			args.append(np)
			
		elif cmd == 'c':
			dnp = args.pop()
			dc1 = args.pop()
			dc0 = args.pop()
			cp = args.pop()
			
			c1 = cp + dc1
			c0 = cp + dc0
			np = cp + dnp
						
			parts.append(Bezier3(cp, c0, c1, np));
			cmd = 'c'
			args.append(np)
		
		elif cmd == 'C':
			np = args.pop()
			c1 = args.pop()
			c0 = args.pop()
			cp = args.pop()
						
			parts.append(Bezier3(cp, c0, c1, np));
			cmd = 'C'
			args.append(np)
				
		else:
			fail("ERROR: unknown command: {}".format(cmd))
	
	return parts
		
	
	
	
def read_svg(fname):
	"""
	
	TODO: This will convert everything to mm
	
	return -- obrys:Path, profil:Path, to_mm, mm_to (1mm experssed in pixels; mm/px ratio)
	"""
	
	info("opening {!r}".format(fname))
	import xml.etree.ElementTree as ET
	tree = ET.parse(fname)
	root = tree.getroot()
	
	x0,y0,x1,y1 = accept_viewBox(Reader(root.get('viewBox')))
	dx = x1 - x0
	dy = y1 - y0
	
	width_mm = accept_mm(Reader(root.get('width')))
	height_mm = accept_mm(Reader(root.get('height')))
	
	to_mmx = width_mm/dx
	to_mmy = height_mm/dy
	assert math.isclose(to_mmx, to_mmy), (to_mmx, to_mmy)
	to_mm = to_mmx
	mm_to = dx/width_mm
	
	info("width:  {:.1f} [mm]".format(width_mm))
	info("height: {:.1f} [mm]".format(height_mm))
	
	info("scale: 1mm is {:.3f}u".format(mm_to))
	
	profil = root.find(".//*[@id='profil']")	
	if profil is None:
		warning("nie znalazlem profilu na rysunku")
	
	obrys = root.find(".//*[@id='obrys']")
	if obrys is None:
		warning("nie znalazlem obrysu na rysunku")
	
	if obrys is None or profil is None:
		fail("ERROR: brak profilu i/lub obrysu")
		
	profil_path = make_path(accept_path(Reader(profil.get('d'))))
	obrys_path = make_path(accept_path(Reader(obrys.get('d'))))
	
	return Path(obrys_path), Path(profil_path), to_mm, mm_to, (x0,y0,x1,y1)
	
	
	

EXAMPLE_SVG = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   width="210mm"
   height="297mm"
   viewBox="0 0 744.09448819 1052.3622047"
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
     id="obrys"
     d="m 637.66015,793.73082 c 5.43394,164.90634 -450.24462,166.80036 -452.60493,4.45916 L 274.23846,187.2848 c 138.83319,51.23034 359.83833,368.68082 363.42169,606.44602 z"
     style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
  <path
     id="path3365"
     d="m 133.77486,818.25621 539.55858,0"
     style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
  <path
     id="profil"
     d="M 671.10386,816.02663 C 628.88531,741.3421 437.94884,710.4192 354.50337,762.51668 280.17856,664.68941 178.47055,672.09174 131.54528,816.02663"
     style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1;image-rendering:auto" />
</svg>
"""


def test():
	#import pdb; pdb.set_trace()
	#print accept_point(Reader("1.0,2.0"))
	
	import io
	
	obrys, profil, mm = read_svg(io.StringIO(EXAMPLE_SVG))

	obrys = Path(obrys).flattern()
	profil = Path(profil).flattern()

	
	import matplotlib.pyplot as plt
	
	obrys.render(plt)
	profil.render(plt)
	
	plt.show()
	
	
	
	
	
	
	
		
if __name__ == '__main__':
	test()
	
 
 

