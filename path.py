import numpy as np
import math
from reader import Reader
from log import fail, info, warning


def Vec(*col):
	return np.array(col)
	
def Mat(rows, cols):
	"""	
	>>> print(Mat([Vec(1,2),Vec(3,4)], None))
	[[1 2]
	 [3 4]]
	>>> print(Mat(None, [Vec(1,2),Vec(3,4)]))
	[[1 3]
	 [2 4]]
	"""
	if rows is None:
		return np.array(cols).T
	else:
		assert cols is None
		return np.array(rows)
	
def det(A):
	"""	
	>>> det(Mat(None, [Vec(1,2),Vec(3,4)]))
	-2
	"""
	assert A.shape == (2,2)
	a = A[0][0]; b = A[0][1]
	c = A[1][0]; d = A[1][1]
	
	return a*d - c*b
	
def adj(A):
	"""	
	>>> print(adj(Mat(None, [Vec(1,2),Vec(3,4)])))
	[[ 4 -3]
	 [-2  1]]
	"""
	assert A.shape == (2,2)
	a = A[0][0]; b = A[0][1]
	c = A[1][0]; d = A[1][1]	
	return Mat(rows=[[d,-b],[-c,a]], cols=None)


def project(point, line):
	""" Project 'point onto the 'line
	return -- point, h_line
	
	>>> p,h = project( Vec(0,2), Line( Vec(0,0), Vec(2,2) ))
	>>> assert (p == Vec(1,1)).all()
	>>> assert h == 0.5	
	>>> p,h = project( Vec(5,7), Line( Vec(6,8), Vec(1,8) ))  # regress
	>>> assert (p == Vec(5,8)).all()
	>>> assert h == 0.2	
	"""
	x0 = line.p0
	x1 = line.p1
	v = point - x0
	s = x1 - x0
	h = v.dot(s)/s.dot(s)
	return h * s + x0, h


def distance(a,b):
	""" Distance beetween points 'a and 'b 
	
	>>> distance(Vec(1,2),Vec(4,6))
	5.0
	>>> distance(Vec(4,6),Vec(1,2))
	5.0
	>>> distance(Vec(0,0),Vec(0,0))
	0.0
	"""
	dv = b - a
	return math.sqrt(dv.dot(dv))
	
	
def get_lengths(xs):
	for i in range(len(xs) - 1):
		yield distance(xs[i], xs[i+1])
	
	
class Poly:
	def __init__(self, xs):
		self.xs = xs
		self.ls = list(get_lengths(xs))
	
	def get_length(self):
		return sum(self.ls)
		
	def get_vertex(self, i):
		return self.xs[i]
	
	def get_section_length(self, i):
		"""
		>>> p = Poly([Vec(0,0), Vec(-3,-4)])
		>>> assert p.get_section_length(0) == 5
		"""
		return self.ls[i]
		
	def join(self, poly):
		p = Poly([])
		p.extend(self.xs)
		p.extend(poly.xs)
		return p
		
	def extend(self, xs):
		"""
		>>> p = Poly([Vec(0,0),Vec(0,1)])
		>>> p.extend([Vec(0,1),Vec(0,3)])
		>>> print(p.xs)
		[array([0, 0]), array([0, 1]), array([0, 3])]
		>>> print(p.ls)
		[1.0, 2.0]
		"""
		if len(xs) > 0:
			assert (self.xs[-1] == xs[0]).all()
			self.xs.extend(xs[1:])
			self.ls.extend(get_lengths(xs))
	
	def size(self):
		""" Number of sections """
		return len(self.ls)
			
	def is_empty(self):
		return len(self.ls) == 0
	
	def is_closed(self):
		if self.is_empty():
			return True
		else:
			return self.xs[0] == self.xs[-1]
	
	def get_point(self, d):
		""" Return 'point laying on the curve at a distance 'd measured along the curve
		d -- if d is greater then length of the poly of negative the point will circle around the poly
		return -- point
		
		>>> p = Poly([Vec(0,0), Vec(1,0), Vec(1,1), Vec(0,1)])
		>>> print(p.get_point(0.0))
		[ 0.  0.]
		>>> print(p.get_length())
		3.0
		>>> print(p.get_point(p.get_length()))
		[ 0.  1.]
		>>> print(p.get_point(3.0))
		[ 0.  1.]
		"""
		
		if self.is_empty():
			return None
				
		#while d < 0:
		#	d += self.get_length()
		
		
		for i in range(0, self.size()):
			# current section xs[i],xs[i+1]
			# current section length ls[i]
			
			sect_len = self.ls[i]
			x0 = self.xs[i]
			x1 = self.xs[i+1]
			
			if d < sect_len or math.isclose(d, sect_len):
				return get_point_line(x0, x1, d/sect_len)
				
			else:			
				d -= sect_len
		
		return None
			
			
	def render(self, plt):
		ps = []
		for x in self.xs:
			ps.append(x)
			
		ps = np.array(ps).transpose()
		return plt.plot(ps[0], ps[1])	
			
				
				


def get_point_line(x0, x1, t):
	""" Point at t
	
	>>> get_point_line(Vec(0,0), Vec(1,0), 0.0)
	array([ 0.,  0.])
	>>> get_point_line(Vec(0,0), Vec(1,0), 1.0)
	array([ 1.,  0.])
	>>> get_point_line(Vec(0,0), Vec(1,0), 0.25)
	array([ 0.25,  0.  ])
	"""
	h = 1.0 - t
	p = x0 * h + x1 * t
	return p
			


class Bezier1:
	def __init__(self, p0, p1):
		""" Bezier1 is simply a section """
		self.p0 = p0
		self.p1 = p1
				
	def get_point(self, t):
		""" Point at t
		
		>>> b = Bezier1(Vec(0,0), Vec(1,0))
		>>> b.get_point(0)
		array([ 0.,  0.])
		>>> b.get_point(1)
		array([ 1.,  0.])
		>>> b.get_point(0.25)
		array([ 0.25,  0.  ])
		"""
		return get_point_line(self.p0, self.p1, t)
				
	def get_length(self):
		""" Length """
		return distance(self.p1, self.p0)
				
	def get_dir(self):
		return self.p1 - self.p0
			
	def __repr__(self):
		return "Bezier1({},{})".format(self.p0, self.p1)

	def render(self, plt):
		ps = [self.p0, self.p1]
		ps = np.array(ps).transpose()
		return plt.plot(ps[0], ps[1])
		
class Line(Bezier1):
	""" infinite line """
	pass

class Bezier3:
	def __init__(self, p0, p1, p2, p3):
		""" Defined by control points """		
		self.mt = Mat(None, [p0, 3 * p1, 3 * p2, p3])
				
	def get_point(self, t):
		""" Point at t"""
		h = 1.0 - t
		v = Vec(h*h*h, h*h*t, h*t*t, t*t*t)		
		p = self.mt.dot(v)
		return p
	


def flattern_bezier_list(parts, tolerance):
	""" Return error and list of vertices
	"""
	max_err = 0.0
	points = []		
	for part in parts:
		if type(part) == Bezier3:
			err, ps = flattern_bezier3(part, tolerance)
			max_err = max(max_err, err)
			
		elif type(part) == Bezier1:
			ps = [part.p0, part.p1]
		
		else:
			fail("ERROR: unknown part type")
			
		
		if points:
			assert (points[-1] == ps[0]).all()
			points.extend(ps[1:])
		else:
			assert len(ps[0]) == 2
			points.extend(ps)
		
							
	return max_err, points

def flattern_bezier3_n(b3, n):
	""" Return error and list of vertices 
	n -- number of sections to aproximate with
	"""
	points = []
	
	max_err = 0.0
	t0 = float(0)/n 
	x0 = b3.get_point(t0)
	
	points.append(x0)
	for i in range(0,n):
		t1 = float(i+1)/n
		x1 = b3.get_point(t1)			
		
		# B3 range [t0,t1] corresponding to [x0,x1] points
				
		# test points			
		e = distance(get_point_line(x0, x1, 0.33), b3.get_point(0.67 * t0 + 0.33 * t1))
		if e > max_err:
			max_err = e
		
		e = distance(get_point_line(x0, x1, 0.50), b3.get_point(0.50 * t0 + 0.50 * t1))
		if e > max_err:
			max_err = e		
			
		e = distance(get_point_line(x0, x1, 0.67), b3.get_point(0.33 * t0 + 0.67 * t1))
		if e > max_err:
			max_err = e
		
		t0 = t1
		x0 = x1
		points.append(x0)
		
	return max_err, points

def flattern_bezier3(b3, tolerance):
	""" Return error and list of vertices 
	tolerance -- max allowed error
	"""
	for n in range(1,16000):
		err, points = flattern_bezier3_n(b3, n)
		if err <= tolerance:
			#info("aproximating curve with {} sections".format(n))
			return err, points
			
	fail("ERROR: cannot approximate curve; err={}; tol={}".format(err, tolerance))

	
	



def intersect_line_line(x1,x2, y1,y2):
	"""
	x1,x2 -- two points defining first line
	y1,y2 -- two points defining second line
	return -- [(t_01, h_01)] or []
		
	>>> intersect_line_line(Vec(0,0), Vec(4,4), Vec(2,0), Vec(0,2))
	[(0.25, 0.5)]
	>>> intersect_line_line(Vec(0,0), Vec(2,0), Vec(0,2), Vec(2,2))
	[]
	"""
	
	A = Mat(cols=[x2 - x1, -y2 + y1], rows=None)	
	B = -x1 + y1
	
	d = det(A)
	if d == 0:
		return []
		
	t,h = (adj(A).dot(B))/d
	
	return [(round(t,12),round(h,12))]
	
	
	
def intersect_poly_poly(a,b):	
	"""
	return -- list of (t_len, h_len)
	
	>>> a = Poly([Vec(2,0), Vec(0,0), Vec(0,2)])
	>>> b = Poly([Vec(-1,-1), Vec(1,1)])
	>>> r = intersect_poly_poly(a,b)
	>>> assert r == [(2.0, math.sqrt(2))], r
	"""
	assert type(a) == Poly and type(b) == Poly
	
	rs = []	
	
	xp = 0.0
	
	for i in range(a.size()):
	
		x1 = a.get_vertex(i)
		x2 = a.get_vertex(i+1)
		xl = a.get_section_length(i)
	
		yp = 0.0
		for j in range(b.size()):
			
			y1 = b.get_vertex(j)
			y2 = b.get_vertex(j+1)
			yl = b.get_section_length(j)
			
			ths = intersect_line_line(x1,x2, y1,y2)
			if ths:
				t,h = ths[0]
				if 0 <= t <= 1 and 0 <= h <= 1:
					r = (xp + t*xl, yp + h*yl)
					
					if len(rs) == 0 or (rs and rs[-1] != r):
						rs.append(r)
			
			yp += yl
			
		xp += xl
	
	return rs
	
			
	

	
def intersect_poly_line(poly, line):
	"""
	return list of (t_len, h_01)
	
	>>> p = Poly([Vec(0,2), (100,2)])
	>>> l = Line(Vec(50,0), Vec(50, -1))
	>>> print(intersect_poly_line(p, l))
	[(50.0, -2.0)]
	"""
	assert type(poly) == Poly
	assert type(line) == Line
	
	y1 = line.p0
	y2 = line.p1
	
	rs = []	
	
	xp = 0.0
	for i in range(poly.size()):
	
		x1 = poly.get_vertex(i)
		x2 = poly.get_vertex(i+1)
		xl = poly.get_section_length(i)
	
		ths = intersect_line_line(x1,x2, y1,y2)
		
		if ths:
			t,h = ths[0]
			if 0.0 <= t <= 1.0:
			
				r = (xp + t*xl, h)
				if len(rs) == 0 or (rs and rs[-1] != r):
					rs.append(r)
		
		xp += xl
	
	return rs
	








def test():
	import matplotlib.pyplot as plt
	c = Bezier3(
		Vec(120,160),
		Vec(35,200),
		Vec(220,260),
		Vec(220,40),
	)

	ps = []
	for i in range(0,51):
		t = (i)/50.0	
		p = c.get_point(t)
		ps.append(p)

	ps = np.array(ps).transpose()
	plt.plot(ps[0], ps[1])
	
	
	ps = []
	xs = c.flattern(6)
		
	if xs:
		ps.append(xs[0].get_point(0))
		
	for x in xs:
		ps.append(x.get_point(1))
	
	ps = np.array(ps).transpose()
	plt.plot(ps[0], ps[1])
	plt.show()
	

if __name__ == '__main__':
	test()
