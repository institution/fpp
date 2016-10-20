import io

class Reader:
	def __init__(self, src):
		"""if isinstance(src, str):
			self.src = io.StringIO(src)
		else:
		"""
		
		self.src = src
		self.i = 0
	
	def get_ind(self):
		return self.i
	
	def get(self):
		if self.i < len(self.src):
			c = self.src[self.i]
			# print(c, end='')
			self.i += 1	
			return c
		else:
			return "TERMINAL"			
	
	def peek(self):
		if self.i < len(self.src):
			c = self.src[self.i]
			return c
		else:
			return "TERMINAL"
	
