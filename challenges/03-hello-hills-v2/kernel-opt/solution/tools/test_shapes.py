#!/usr/bin/env python3
"""Correctness sweep over many n (including primes / non-multiples of MR,NR)."""
import ctypes, subprocess, tempfile, pathlib, numpy as np
src = pathlib.Path(__file__).resolve().parent.parent / "kernel.c"
td = tempfile.mkdtemp(); so = pathlib.Path(td) / "k.so"
subprocess.run(["cc", str(src), "-o", str(so), "-O3", "-march=native", "-ffast-math",
                "-shared", "-fPIC", "-lm"], check=True)
lib = ctypes.CDLL(str(so)); f32p = ctypes.POINTER(ctypes.c_float)
lib.gemm.restype = None; lib.gemm.argtypes = [ctypes.c_int, f32p, f32p, f32p]
rng = np.random.default_rng(0); bad = 0
for n in [1, 2, 3, 7, 8, 11, 12, 13, 17, 31, 64, 96, 97, 127, 128, 129, 200, 256, 257,
          383, 384, 511, 512, 513, 640, 1024]:
    a = np.ascontiguousarray(rng.standard_normal((n, n), dtype=np.float32))
    b = np.ascontiguousarray(rng.standard_normal((n, n), dtype=np.float32))
    c = np.zeros((n, n), dtype=np.float32)
    lib.gemm(n, a.ctypes.data_as(f32p), b.ctypes.data_as(f32p), c.ctypes.data_as(f32p))
    w = a @ b
    e = float(np.max(np.abs(c - w)) / (np.max(np.abs(w)) + 1e-9))
    ok = np.isfinite(c).all() and e <= 2e-3
    bad += not ok
    print(f"n={n:<5} relerr={e:.3e} {'OK' if ok else 'FAIL'}")
print("ALL OK" if not bad else f"{bad} FAILURES")
