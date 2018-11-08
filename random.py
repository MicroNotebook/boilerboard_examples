def randomInt_help(x, y, z, w, v):
    t = (int(x) ^ (int(x) >> 7))
    x = y
    y = z
    z = w
    w = v
    v = (v ^ (v << 6)) ^ (t ^ (t << 13))
    n = (y + y + 1) * v
    return n, x, y, z, w, v

def randomInt(lb, ub, x, y, z, w, v):
    n, x, y, z, w, v = randomInt_help(x, y, z, w, v)
    n = (n % (ub - lb + 1)) + lb
    return n, x, y, z, w, v
