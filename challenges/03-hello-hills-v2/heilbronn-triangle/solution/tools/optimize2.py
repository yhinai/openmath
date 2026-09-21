"""Basin-hopping maximin search (SLP inner solver with line search)."""
import sys, json, itertools, numpy as np, time
from scipy.optimize import linprog

N = 11
SEED = int(sys.argv[1]); OUT = sys.argv[2]; TLIM = float(sys.argv[3])
S3 = np.sqrt(3.0); AREA = S3 / 2.0
TRIPLES = np.array(list(itertools.combinations(range(N), 3)))
T = len(TRIPLES)
I0, I1, I2 = TRIPLES[:, 0], TRIPLES[:, 1], TRIPLES[:, 2]
IDX = np.arange(T)

def dets(P):
    a, b, c = P[I0], P[I1], P[I2]
    return (b[:,0]-a[:,0])*(c[:,1]-a[:,1]) - (c[:,0]-a[:,0])*(b[:,1]-a[:,1])

def score(P):
    return np.abs(dets(P)).min()/AREA

def grads(P):
    G = np.zeros((T, N, 2)); a,b,c = P[I0],P[I1],P[I2]
    G[IDX,I0,0] = b[:,1]-c[:,1]; G[IDX,I0,1] = c[:,0]-b[:,0]
    G[IDX,I1,0] = c[:,1]-a[:,1]; G[IDX,I1,1] = a[:,0]-c[:,0]
    G[IDX,I2,0] = a[:,1]-b[:,1]; G[IDX,I2,1] = b[:,0]-a[:,0]
    return G

def rand_point(rng):
    while True:
        x, y = rng.random(), rng.random()*(S3/2)
        if y <= S3*x and y <= S3*(1-x): return x, y

def clip_in(P):
    P = np.atleast_2d(np.array(P,dtype=float)).copy(); P[:,1] = np.maximum(P[:,1], 0.0)
    for i in range(len(P)):
        x,y = P[i]
        if y > S3*x:      # project onto left edge
            t = (x + y/S3)/2; P[i] = [t, S3*t]
        x,y = P[i]
        if y > S3*(1-x):
            t = ((1-x) + y/S3)/2; P[i] = [1-t, S3*t]
    return P

def slp(P, iters=400):
    tr = 0.03; best = score(P); bestP = P.copy()
    for it in range(iters):
        d = dets(P); s = np.sign(d); s[s==0]=1.0
        G = grads(P)*s[:,None,None]
        A = np.zeros((T+3*N, 2*N+1)); b = np.zeros(T+3*N)
        A[:T,:2*N] = -G.reshape(T,2*N); A[:T,2*N] = 1.0; b[:T] = s*d
        for i in range(N):
            x,y = P[i]; r = T+3*i
            A[r,2*i+1] = -1.0; b[r] = y
            A[r+1,2*i+1] = 1.0; A[r+1,2*i] = -S3; b[r+1] = S3*x - y
            A[r+2,2*i+1] = 1.0; A[r+2,2*i] = S3;  b[r+2] = S3*(1-x) - y
        c = np.zeros(2*N+1); c[2*N] = -1.0
        res = linprog(c, A_ub=A, b_ub=b, bounds=[(-tr,tr)]*(2*N)+[(None,None)], method="highs")
        if not res.success:
            tr *= 0.5
            if tr < 1e-14: break
            continue
        step = res.x[:2*N].reshape(N,2)
        improved = False
        for al in (1.0, 0.5, 0.25, 0.1, 0.03):
            Q = clip_in(P + al*step); sc = score(Q)
            if sc > best*(1+1e-15):
                best, bestP, P = sc, Q.copy(), Q; improved = True
                break
        if improved:
            tr = min(tr*1.5, 0.05)
        else:
            tr *= 0.4
            if tr < 1e-15: break
            P = bestP.copy()
    return best, bestP

def main():
    rng = np.random.default_rng(SEED)
    t0 = time.time(); gbest, gP = -1.0, None
    if len(sys.argv) > 4:
        gP = np.array([[float(a), float(b)] for a, b in json.load(open(sys.argv[4]))])
        if isinstance(gP, np.ndarray) and gP.shape == (N, 2):
            gbest = score(gP)
            print("seeded", gbest, flush=True)
    while time.time()-t0 < TLIM:
        if gP is None or rng.random() < 0.10:
            P = np.array([rand_point(rng) for _ in range(N)])
        else:
            P = gP.copy()
            k = rng.integers(1,3)
            for i in rng.choice(N, size=k, replace=False):
                if rng.random() < 0.5: P[i] = rand_point(rng)
                else: P[i] = clip_in((P[i]+rng.normal(0,0.05,2))[None,:])[0]
        sc, P = slp(P)
        if sc > gbest:
            gbest, gP = sc, P.copy()
            json.dump({"score":gbest,"points":gP.tolist()}, open(OUT,"w"))
            print(f"{time.time()-t0:7.1f}s new best {gbest:.12f}", flush=True)
main()
