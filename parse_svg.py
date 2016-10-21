from reader import Reader
from path import Bezier1, Bezier3, Vec, fail, Line
import sys, math
from log import fail, info, warning

	
	

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
	"""
	return -- list of beziers
	"""
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
		
	

	
def is_arrow(path):
	return len(path.parts) == 2 and is_poly(path)

def get_arrowhead(path):
	assert is_arrow(path)
	return path.parts[0].get_point(1.0)

	

	
	
	
	
	
		
if __name__ == '__main__':
	test()
	
 
 

