import random
import string
import sys
import os

random.seed()

for i in range(1,90000000):

	print("%s %s" % ('b', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))))
