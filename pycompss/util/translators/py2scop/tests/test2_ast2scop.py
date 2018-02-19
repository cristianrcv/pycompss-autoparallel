# Single loop with different header / footer options
def simple1(a, b, c):
        print "HEADER"
        for i in range(1, 10, 1):
                c = c + a*b
        print "FOOTER"


def simple2(a, b, c):
        for i in range(1, 10, 1):
                c = c + a*b
        print "FOOTER"


def simple3(a, b, c):
        print "HEADER"
        for i in range(1, 10, 1):
                c = c + a*b


def simple4(a, b, c):
        for i in range(1, 10, 1):
                c = c + a*b


# 2 loops with different intermediate options
def intermediate1(a, b, c):
        print "HEADER"
        for i1 in range(1, 10, 1):
                c = c + a*b
        for i2 in range(1, 10, 1):
                c = c + a*b
        print "FOOTER"


def intermediate2(a, b, c):
        print "HEADER"
        for i1 in range(1, 10, 1):
                c = c + a*b
        # A comment
        for i2 in range(1, 10, 1):
                c = c + a*b
        print "FOOTER"


def intermediate3(a, b, c):
        print "HEADER"
        for i1 in range(1, 10, 1):
                c = c + a*b
        print "INTER"
        for i2 in range(1, 10, 1):
                c = c + a*b
        print "FOOTER"


# Different loop nests
def loop_nests1(a, b, c):
        print "HEADER"
        for i1 in range(1, 10, 1):
                for j1 in range(1, 20, 1):
                        c = c + a*b
        print "FOOTER"


def loop_nests2(a, b, c):
        print "HEADER"
        for i1 in range(1, 2*N-M+K, 1):
                for j1 in range(1, M, 1):
                        c[i1][j1] = c[i1][j1] + a[i1][j1]*b[i1][M-j1]
                for j2 in range(1, M, 1):
                        for k1 in range(1, K, 1):
                                c = c + a*b
                        c = c + a*b
        print "FOOTER"


# Complex test
def complex(a, b, c):
        print "HELLO"
        for i1 in range(1, 10, 1):
                for j1 in range(1, 20, 1):
                        c = c + a*b
                for j2 in range(1, 30, 1):
                        for k1 in range(1, 40, 1):
                                c = c + a*b
        for i2 in range(1, 50, 1):
                c = c + a*b
        print "INTER"
        for i3 in range(1, 60, 1):
                c = c + a*b
        print "INTER2"
        if a != b:
                for i4 in range(1, 70, 1):
                        c = c + a*b
        print "BYE"
