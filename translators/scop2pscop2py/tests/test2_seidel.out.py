import math
def S1(zT3,zT4,zT5,t,i,j):
	a[i][j] = (a[i-1][j-1] + a[i-1][j] + a[i-1][j+1] + a[i][j-1] + a[i][j] + a[i][j+1] + a[i+1][j-1] + a[i+1][j] + a[i+1][j+1])/9.0;

# Start of CLooG code
if ((N >= 3) and (T >= 1)):
        lbp=0
        ubp=int(math.floor(2*T+N-4,32))
        for t1 in range(0, int(math.floor(2*T+N-4,32))):
                lbp=max(int(math.ceil(t1,2)),int(math.ceil(32*t1-T+1,32)))
                ubp=min(min(int(math.floor(T+N-3,32)),int(math.floor(32*t1+N+29,64))),t1)
                # parallel for
                for t2 in range(lbp, ubp):
                        lbp=max(int(math.ceil(64*t2-N-28,32)),t1)
                        ubp=min(min(min(min(int(math.floor(T+N-3,16)),int(math.floor(32*t1-32*t2+N+29,16))),int(math.floor(32*t1+N+60,32))),int(math.floor(64*t2+N+59,32))),int(math.floor(32*t2+T+N+28,32)))
                        for t3 in range(max(int(math.ceil(64*t2-N-28,32)),t1), min(min(min(min(int(math.floor(T+N-3,16)),int(math.floor(32*t1-32*t2+N+29,16))),int(math.floor(32*t1+N+60,32))),int(math.floor(64*t2+N+59,32))),int(math.floor(32*t2+T+N+28,32)))):
                                lbp=max(max(max(32*t1-32*t2,32*t2-N+2),16*t3-N+2),-32*t2+32*t3-N-29)
                                ubp=min(min(min(min(T-1,32*t2+30),16*t3+14),32*t1-32*t2+31),-32*t2+32*t3+30)
                                for t4 in range(max(max(max(32*t1-32*t2,32*t2-N+2),16*t3-N+2),-32*t2+32*t3-N-29), min(min(min(min(T-1,32*t2+30),16*t3+14),32*t1-32*t2+31),-32*t2+32*t3+30)):
                                        lbp=max(max(32*t2,t4+1),32*t3-t4-N+2)
                                        ubp=min(min(32*t2+31,32*t3-t4+30),t4+N-2)
                                        for t5 in range(max(max(32*t2,t4+1),32*t3-t4-N+2), min(min(32*t2+31,32*t3-t4+30),t4+N-2)):
                                                lbp=max(32*t3,t4+t5+1)
                                                ubp=min(32*t3+31,t4+t5+N-2)
                                                for t6 in range(max(32*t3,t4+t5+1), min(32*t3+31,t4+t5+N-2)):
                                                        S1((t1-t2),t2,t3,t4,(-t4+t5),(-t4-t5+t6))
# End of CLooG code
