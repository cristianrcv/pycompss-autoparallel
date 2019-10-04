def matmul(a, b, c, m_size, alpha, beta, debug):
    # Debug
    if debug:
        print("Matrix A:")
        print(a)
        print("Matrix B:")
        print(b)
        print("Matrix C:")
        print(c)

    # Matrix multiplication
    for i in range(m_size):
        for j in range(m_size):
            # c[i][j] *= beta
            c[i][j] = scale(c[i][j], beta)
        for k in range(m_size):
            for j in range(m_size):
                # c[i][j] += alpha * a[i][k] * b[k][j]
                c[i][j] = multiply(c[i][j], alpha, a[i][k], b[k][j])

    # Debug
    if debug:
        print("Matrix C:")
        print(c)

    # Result
    return c


def multiply(c, alpha, a, b):
    return c + alpha * a * b


def scale(c, beta):
    return c * beta
