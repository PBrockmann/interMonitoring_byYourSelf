#!/usr/bin/env python

import numpy as np

#===========================================================
def sbx(array, windowsize):
    """
    Perform smoothing box 
    """
    
    w=int(windowsize/2.)
    b=np.ma.copy(array)
    l=len(array)
    for i in range(l) :
    		if i+1 <= w or i+1 > l-w :
    			b[i]=np.ma.masked
    		else :
    			ave=array[i-w:i+w+1]
    			b[i]=np.average(ave)
    
    return b

#===========================================================

#a=np.ma.array([12,34,45,10,78,56])
a=np.ma.array(np.random.randint(0,100,size=20))

print a

b=sbx(a,3)
print b
b=sbx(a,5)
print b

print np.ma.masked_where(b<=-1E+34,b)

