from __future__ import division
import math
import re

# Redefining the only function that makes the calculator crash
def factorial(n):
    fact = 1
    while (n > 0):
        fact *= n
        n -= 1
        if float(fact) > 1e100:
            return 0
    return fact

# Math functions
safe_list = ['acos', 'asin', 'atan', 'atan2', 'cos', 'cosh', 'degrees', 'e', 'erf', 'exp', 'fabs', 'hypot', 'log', 'log10', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh'] 
 
# Create safe directory
safe_dict = dict((k, getattr(math, k)) for k in safe_list)
safe_dict['float'] = float
safe_dict['factorial'] = factorial

# Checks if any of the characters in set are in string
def contains(string, set):
    return 1 in [c in string for c in set]

# Use float casts to avoid expensive computations
def fix(expression):
	regex = re.compile('(?P<num>[-]?([0-9]*\.)?[0-9]+)') # Detect numbers
	return regex.sub('float(' + '\g<num>' + ')', expression)

# Evaluate mathematical expression from string
def calculate(expression):
	if contains(expression, '_\'\"[];'):
		return 0

	expression = expression.replace('^', '**')
	fixed = fix(expression)

	try:
		result = eval(fixed, {"__builtins__": None}, safe_dict)
		if -1e-10 < result < 1e-10:
			return 0
		elif -1e-10 < int(result) - result < 1e-10:
			return int(result)
		else:
			return result

	except Exception, ex:
		print ex
		return 0
