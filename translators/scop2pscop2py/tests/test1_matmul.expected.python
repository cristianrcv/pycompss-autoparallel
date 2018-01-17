import math
def S1(zT3,zT4,zT5,i,j,k):
	c[i][j] += a[i][k]*b[k][j];

# Start of CLooG code
if ((kSize >= 1) and (mSize >= 1) and (nSize >= 1)):
        lbp=0
        ubp=int(math.floor(float(mSize-1)/float(32)))
        # parallel for
        for t1 in range(lbp, ubp):
                lbp=0
                ubp=int(math.floor(float(kSize-1)/float(32)))
                for t2 in range(0, int(math.floor(float(kSize-1)/float(32)))):
                        lbp=0
                        ubp=int(math.floor(float(nSize-1)/float(32)))
                        for t3 in range(0, int(math.floor(float(nSize-1)/float(32)))):
                                lbp=32*t1
                                ubp=min(mSize-1,32*t1+31)
                                for t4 in range(32*t1, min(mSize-1,32*t1+31)):
                                        lbp=32*t3
                                        ubp=min(nSize-1,32*t3+31)
                                        for t5 in range(32*t3, min(nSize-1,32*t3+31)):
                                                lbp=32*t2
                                                ubp=min(kSize-1,32*t2+31)
                                                # parallel for
                                                for t6 in range(lbv, ubv):
                                                        S1(t1,t2,t3,t4,t6,t5)
# End of CLooG code
