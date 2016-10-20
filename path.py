import numpy as np
import math

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
	"""
	>>> print(project(Vec(0,2),Bezier1(Vec(0,0),Vec(2,2))))
	[ 1.  1.]
	>>> print(project(Vec(5,7),Bezier1(Vec(6,8),Vec(1,8))))  # regress
	[ 5.  8.]
	"""
	v = point - line.p0
	s = line.get_dir()
	return (v.dot(s)/s.dot(s)) * s + line.p0
	

	
def intersect(path,line):
	for part in path.parts:
		t,h = intersect2(line, part)
		if t != None and 0 <= h <= 1:
			return line.get_point(t)
	return None

def intersect2(a,b):
	"""
	a -- bezier1
	b -- bezier1
	return -- (t, h)|(None,None)
		
	>>> intersect2(Bezier1(Vec(0,0),Vec(4,4)), Bezier1(Vec(2,0),Vec(0,2)))
	(0.25, 0.5)
	>>> intersect2(Bezier1(Vec(0,0),Vec(2,0)), Bezier1(Vec(0,2),Vec(2,2)))
	(None, None)
	"""
	x1 = a.p0
	x2 = a.p1
	y1 = b.p0
	y2 = b.p1
	

	A = Mat(cols=[x2 - x1, -y2+y1], rows=None)
	
	B = -x1 + y1
	d = det(A)
	if d == 0:
		return (None,None)
		
	t,h = (adj(A).dot(B))/d
	
	return (t,h)
	
		
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
	
	
	
class Path:
	def __init__(self, parts):
		self.parts = parts
		
	
	def get_point(self, d):
		""" Return 'point laying on the curve at a distance 'd measured along the curve
		d -- allowed range: [0, curve_length]  
		return -- 'point|None; will return None if 'd outside allowed range
		"""
		l = 0
		for part in self.parts:
			pl = part.get_length()
			if d <= l + pl:
				# point is in this section
				return part.get_point((d - l) / pl)
										
			l += pl
		return None
		
		
	def get_length(self):
		"""
		>>> Path([]).get_length()
		0.0
		"""
		l = 0.0
		for p in self.parts:
			l += p.get_length()
		return l
	
	def flattern(self):
		# TODO: some kind of approx error control
		r = Path([])
		for part in self.parts:
			if isinstance(part, Bezier3):
				for p in part.flattern(14):
					r.parts.append(p)
			else:
				r.parts.append(part)
				
		return r
				
	def render(self, plt):
		ps = []
		if self.parts:
			ps.append(self.parts[0].get_point(0))
		
		for part in self.parts:
			ps.append(part.get_point(1))
			
		ps = np.array(ps).transpose()
		return plt.plot(ps[0], ps[1])
		
		
class Bezier1:
	def __init__(self, p0, p1):
		""" Bezier1 is simply a line """
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
		h = 1.0 - t
		p = self.p0 * h + self.p1 * t
		return p
				
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
	
	def flattern(self, n):
		parts = []
		t0 = float(0)/n 
		p0 = self.get_point(t0)
		for i in range(0,n):
			t1 = float(i+1)/n
			p1 = self.get_point(t1)			
			parts.append(Bezier1(p0, p1))			
			t0 = t1
			p0 = p1
		return parts
		
	def get_length(self):
		""" APPROXIMATE length of the curve """
		pass
	

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
