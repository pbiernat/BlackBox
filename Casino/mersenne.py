'''
An implementation of MT19937 Mersenne Twister Random number generator.


Based on Wikipedia PseudoCode as suggested by the challenge.

mtwister will end up being an object (PRNG) with its own state.
-Patrick Biernat
'''



class mtwister(object):
	def __init__(self,seed):
		'''
		Sets up some values and performs initialization from a seed.
		MT array init Code split up for readability, most implementations throw everything
		into one line. 
		'''
		self.MT = [0] * 624
		self.index = 0
		self.MT[0] = int(seed & 0xffffffff)
		for i in range(1,624):
			cnst = (self.MT[i-1] >> 30)
			cnst1 = self.MT[i-1] ^ cnst
			cnst1 = 1812433253 * cnst1
			cnst1 = cnst1 + i
			self.MT[i] = (cnst1 & 0xffffffff) #Get Lower 32 Bits

	def generate_numbers(self):
		'''
		Generate an array of 624 untempered(?) numbers
		'''
		for i in range(0,624):
			y = (self.MT[i] & 0x80000000) + ( (self.MT[(i + 1) % 624]) & 0x7fffffff ) 
			self.MT[i] = self.MT[ (i + 397) % 624] ^ (y >> 1)
			if ( (y % 2) != 0):
				self.MT[i] = self.MT[i] ^ 0x9908b0df
	
	def extract_number(self):
		'''
		Extract a "tempered" number based on index-th value,
		calling generate_numbers every 624 vals.
		'''
		if (self.index == 0):
			self.generate_numbers()
		y = self.MT[self.index]
		y = y ^ (y >> 11)
		y = y ^ ( (y << 7) & 0x9d2c5680 )
	#	print "Y_2 " + str(y)
		y = y ^ ( (y << 15) & 0xefc60000 )
	#	print "Y_1 " + str(y)
		y = y ^ (y >> 18)
		self.index = (self.index + 1) % 624

		return y

'''
Test with Two instances

mt = mtwister(0)
print mt.extract_number()
print mt.extract_number()
print mt.extract_number()

yt = mtwister(0)
print yt.extract_number()
print yt.extract_number()
print yt.extract_number()


'''
