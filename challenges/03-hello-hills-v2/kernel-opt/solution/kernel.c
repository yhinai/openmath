/* Single-threaded row-major SGEMM for AArch64 (NEON), C = A @ B.
 *
 * Structure: classic BLIS-style blocked GEMM.
 *   - cache blocking over (jc=NC, pc=KC, ic=MC)
 *   - A and B blocks packed into contiguous, micro-kernel-ordered buffers
 *   - 8x12 register-blocked micro-kernel using vfmaq_laneq_f32
 *     (24 accumulator vectors + 3 B vectors + 2 A vectors = 29 of 32 regs)
 *
 * No threads, no OpenMP, no BLAS/Accelerate. Pure C + arm_neon.h intrinsics.
 * Falls back to a portable blocked scalar path on non-AArch64 targets.
 */

#include <stdlib.h>
#include <string.h>

#if defined(__aarch64__) || defined(__ARM_NEON)
#define USE_NEON 1
#include <arm_neon.h>
#else
#define USE_NEON 0
#endif

#define MR 8
#define NR 12

#ifndef MC
#define MC 256
#endif
#ifndef KC
#define KC 512
#endif
#ifndef NC
#define NC 512
#endif

#if USE_NEON

/* ---- micro-kernel: C[MR x NR] (+)= pa[MR x kc] * pb[kc x NR] ---- */
static inline void micro_kernel(int kc, const float *restrict pa,
                                const float *restrict pb,
                                float *restrict C, int ldc, int accumulate) {
    float32x4_t c00, c01, c02, c10, c11, c12, c20, c21, c22, c30, c31, c32;
    float32x4_t c40, c41, c42, c50, c51, c52, c60, c61, c62, c70, c71, c72;

    if (accumulate) {
        c00 = vld1q_f32(C + 0 * ldc + 0); c01 = vld1q_f32(C + 0 * ldc + 4); c02 = vld1q_f32(C + 0 * ldc + 8);
        c10 = vld1q_f32(C + 1 * ldc + 0); c11 = vld1q_f32(C + 1 * ldc + 4); c12 = vld1q_f32(C + 1 * ldc + 8);
        c20 = vld1q_f32(C + 2 * ldc + 0); c21 = vld1q_f32(C + 2 * ldc + 4); c22 = vld1q_f32(C + 2 * ldc + 8);
        c30 = vld1q_f32(C + 3 * ldc + 0); c31 = vld1q_f32(C + 3 * ldc + 4); c32 = vld1q_f32(C + 3 * ldc + 8);
        c40 = vld1q_f32(C + 4 * ldc + 0); c41 = vld1q_f32(C + 4 * ldc + 4); c42 = vld1q_f32(C + 4 * ldc + 8);
        c50 = vld1q_f32(C + 5 * ldc + 0); c51 = vld1q_f32(C + 5 * ldc + 4); c52 = vld1q_f32(C + 5 * ldc + 8);
        c60 = vld1q_f32(C + 6 * ldc + 0); c61 = vld1q_f32(C + 6 * ldc + 4); c62 = vld1q_f32(C + 6 * ldc + 8);
        c70 = vld1q_f32(C + 7 * ldc + 0); c71 = vld1q_f32(C + 7 * ldc + 4); c72 = vld1q_f32(C + 7 * ldc + 8);
    } else {
        c00 = c01 = c02 = c10 = c11 = c12 = c20 = c21 = c22 = c30 = c31 = c32 =
        c40 = c41 = c42 = c50 = c51 = c52 = c60 = c61 = c62 = c70 = c71 = c72 =
            vdupq_n_f32(0.0f);
    }

    for (int k = 0; k < kc; ++k) {
        float32x4_t b0 = vld1q_f32(pb + 0);
        float32x4_t b1 = vld1q_f32(pb + 4);
        float32x4_t b2 = vld1q_f32(pb + 8);
        float32x4_t a0 = vld1q_f32(pa + 0);
        float32x4_t a1 = vld1q_f32(pa + 4);
        pa += MR;
        pb += NR;

        c00 = vfmaq_laneq_f32(c00, b0, a0, 0);
        c01 = vfmaq_laneq_f32(c01, b1, a0, 0);
        c02 = vfmaq_laneq_f32(c02, b2, a0, 0);
        c10 = vfmaq_laneq_f32(c10, b0, a0, 1);
        c11 = vfmaq_laneq_f32(c11, b1, a0, 1);
        c12 = vfmaq_laneq_f32(c12, b2, a0, 1);
        c20 = vfmaq_laneq_f32(c20, b0, a0, 2);
        c21 = vfmaq_laneq_f32(c21, b1, a0, 2);
        c22 = vfmaq_laneq_f32(c22, b2, a0, 2);
        c30 = vfmaq_laneq_f32(c30, b0, a0, 3);
        c31 = vfmaq_laneq_f32(c31, b1, a0, 3);
        c32 = vfmaq_laneq_f32(c32, b2, a0, 3);
        c40 = vfmaq_laneq_f32(c40, b0, a1, 0);
        c41 = vfmaq_laneq_f32(c41, b1, a1, 0);
        c42 = vfmaq_laneq_f32(c42, b2, a1, 0);
        c50 = vfmaq_laneq_f32(c50, b0, a1, 1);
        c51 = vfmaq_laneq_f32(c51, b1, a1, 1);
        c52 = vfmaq_laneq_f32(c52, b2, a1, 1);
        c60 = vfmaq_laneq_f32(c60, b0, a1, 2);
        c61 = vfmaq_laneq_f32(c61, b1, a1, 2);
        c62 = vfmaq_laneq_f32(c62, b2, a1, 2);
        c70 = vfmaq_laneq_f32(c70, b0, a1, 3);
        c71 = vfmaq_laneq_f32(c71, b1, a1, 3);
        c72 = vfmaq_laneq_f32(c72, b2, a1, 3);
    }

    vst1q_f32(C + 0 * ldc + 0, c00); vst1q_f32(C + 0 * ldc + 4, c01); vst1q_f32(C + 0 * ldc + 8, c02);
    vst1q_f32(C + 1 * ldc + 0, c10); vst1q_f32(C + 1 * ldc + 4, c11); vst1q_f32(C + 1 * ldc + 8, c12);
    vst1q_f32(C + 2 * ldc + 0, c20); vst1q_f32(C + 2 * ldc + 4, c21); vst1q_f32(C + 2 * ldc + 8, c22);
    vst1q_f32(C + 3 * ldc + 0, c30); vst1q_f32(C + 3 * ldc + 4, c31); vst1q_f32(C + 3 * ldc + 8, c32);
    vst1q_f32(C + 4 * ldc + 0, c40); vst1q_f32(C + 4 * ldc + 4, c41); vst1q_f32(C + 4 * ldc + 8, c42);
    vst1q_f32(C + 5 * ldc + 0, c50); vst1q_f32(C + 5 * ldc + 4, c51); vst1q_f32(C + 5 * ldc + 8, c52);
    vst1q_f32(C + 6 * ldc + 0, c60); vst1q_f32(C + 6 * ldc + 4, c61); vst1q_f32(C + 6 * ldc + 8, c62);
    vst1q_f32(C + 7 * ldc + 0, c70); vst1q_f32(C + 7 * ldc + 4, c71); vst1q_f32(C + 7 * ldc + 8, c72);
}

/* Pack an MR x kc block of A (row-major, lda=n) into k-major micro-panels. */
static void pack_a(int mr, int kc, const float *restrict A, int lda,
                   float *restrict pa) {
    if (mr == MR) {
        const float *a0 = A, *a1 = A + lda, *a2 = A + 2 * lda, *a3 = A + 3 * lda;
        const float *a4 = A + 4 * lda, *a5 = A + 5 * lda, *a6 = A + 6 * lda, *a7 = A + 7 * lda;
        for (int k = 0; k < kc; ++k) {
            pa[0] = a0[k]; pa[1] = a1[k]; pa[2] = a2[k]; pa[3] = a3[k];
            pa[4] = a4[k]; pa[5] = a5[k]; pa[6] = a6[k]; pa[7] = a7[k];
            pa += MR;
        }
    } else {
        for (int k = 0; k < kc; ++k) {
            for (int r = 0; r < mr; ++r) pa[r] = A[r * lda + k];
            for (int r = mr; r < MR; ++r) pa[r] = 0.0f;
            pa += MR;
        }
    }
}

/* Pack a kc x NR block of B (row-major, ldb=n) into k-major micro-panels. */
static void pack_b(int nr, int kc, const float *restrict B, int ldb,
                   float *restrict pb) {
    if (nr == NR) {
        for (int k = 0; k < kc; ++k) {
            vst1q_f32(pb + 0, vld1q_f32(B + 0));
            vst1q_f32(pb + 4, vld1q_f32(B + 4));
            vst1q_f32(pb + 8, vld1q_f32(B + 8));
            pb += NR;
            B += ldb;
        }
    } else {
        for (int k = 0; k < kc; ++k) {
            for (int j = 0; j < nr; ++j) pb[j] = B[j];
            for (int j = nr; j < NR; ++j) pb[j] = 0.0f;
            pb += NR;
            B += ldb;
        }
    }
}

void gemm(int n, const float *A, const float *B, float *C) {
    if (n <= 0) return;

    const int mc = MC, kc_max = KC, nc = NC;

#define ROUND64(x) (((x) + 63u) & ~(size_t)63u)
    float *pa = (float *)aligned_alloc(64, ROUND64((size_t)mc * kc_max * sizeof(float)));
    float *pb = (float *)aligned_alloc(64, ROUND64((size_t)kc_max * nc * sizeof(float)));
    float *ctmp = (float *)aligned_alloc(64, ROUND64((size_t)MR * NR * sizeof(float)));
    if (!pa || !pb || !ctmp) {
        /* graceful fallback: simple correct triple loop */
        free(pa); free(pb); free(ctmp);
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j) {
                float acc = 0.0f;
                for (int k = 0; k < n; ++k) acc += A[i * n + k] * B[k * n + j];
                C[i * n + j] = acc;
            }
        return;
    }

    for (int jc = 0; jc < n; jc += nc) {
        int njc = (n - jc < nc) ? (n - jc) : nc;
        for (int pc = 0; pc < n; pc += kc_max) {
            int kc = (n - pc < kc_max) ? (n - pc) : kc_max;
            int accumulate = (pc != 0);

            /* pack B block: kc x njc */
            int npanels = (njc + NR - 1) / NR;
            for (int p = 0; p < npanels; ++p) {
                int j = p * NR;
                int nr = (njc - j < NR) ? (njc - j) : NR;
                pack_b(nr, kc, B + (size_t)pc * n + jc + j, n, pb + (size_t)p * NR * kc);
            }

            for (int ic = 0; ic < n; ic += mc) {
                int mic = (n - ic < mc) ? (n - ic) : mc;
                int mpanels = (mic + MR - 1) / MR;
                for (int q = 0; q < mpanels; ++q) {
                    int i = q * MR;
                    int mr = (mic - i < MR) ? (mic - i) : MR;
                    pack_a(mr, kc, A + (size_t)(ic + i) * n + pc, n, pa + (size_t)q * MR * kc);
                }

                for (int p = 0; p < npanels; ++p) {
                    int j = p * NR;
                    int nr = (njc - j < NR) ? (njc - j) : NR;
                    for (int q = 0; q < mpanels; ++q) {
                        int i = q * MR;
                        int mr = (mic - i < MR) ? (mic - i) : MR;
                        float *cblk = C + (size_t)(ic + i) * n + jc + j;
                        if (mr == MR && nr == NR) {
                            micro_kernel(kc, pa + (size_t)q * MR * kc,
                                         pb + (size_t)p * NR * kc, cblk, n, accumulate);
                        } else {
                            if (accumulate) {
                                for (int r = 0; r < MR; ++r)
                                    for (int s = 0; s < NR; ++s)
                                        ctmp[r * NR + s] = (r < mr && s < nr) ? cblk[r * n + s] : 0.0f;
                            }
                            micro_kernel(kc, pa + (size_t)q * MR * kc,
                                         pb + (size_t)p * NR * kc, ctmp, NR, accumulate);
                            for (int r = 0; r < mr; ++r)
                                for (int s = 0; s < nr; ++s)
                                    cblk[r * n + s] = ctmp[r * NR + s];
                        }
                    }
                }
            }
        }
    }

    free(pa);
    free(pb);
    free(ctmp);
}

#else /* portable fallback */

void gemm(int n, const float *A, const float *B, float *C) {
    const int BS = 64;
    for (int i = 0; i < n * n; ++i) C[i] = 0.0f;
    for (int ii = 0; ii < n; ii += BS)
        for (int kk = 0; kk < n; kk += BS)
            for (int jj = 0; jj < n; jj += BS) {
                int im = (ii + BS < n) ? ii + BS : n;
                int km = (kk + BS < n) ? kk + BS : n;
                int jm = (jj + BS < n) ? jj + BS : n;
                for (int i = ii; i < im; ++i)
                    for (int k = kk; k < km; ++k) {
                        float a = A[i * n + k];
                        for (int j = jj; j < jm; ++j) C[i * n + j] += a * B[k * n + j];
                    }
            }
}

#endif
