"""Mixture-weight fit (EM) used to choose WEIGHTS in model.py. Paths are the
scratchpad paths used during the run; point them at your own hillcopy to rerun."""
import sys, math
sys.path.insert(0,"/private/tmp/claude-501/-Users-charlie-hackathons-openmath/eff8d621-7309-442b-9162-07db54bf13dc/scratchpad/tune")
import ppm, numpy as np
S="/private/tmp/claude-501/-Users-charlie-hackathons-openmath/eff8d621-7309-442b-9162-07db54bf13dc/scratchpad"
tr=open(S+"/hillcopy/train.txt").read()
val=open(S+"/hillcopy/private/val.txt").read()
A=sorted(set(tr))
KS=[2,3,4,5,6,8]
cnt=ppm.build(tr,max(KS))
get=cnt.get
def dist(prefix,K,esc):
    excl=set(); rem=1.0; out={}
    lp=len(prefix); kk=K if K<=lp else lp
    for k in range(kk,-1,-1):
        d=get(prefix[lp-k:] if k else "")
        if not d: continue
        items=[(c,v) for c,v in d.items() if c not in excl] if excl else list(d.items())
        if not items: continue
        n=0
        for _,v in items: n+=v
        e=esc*len(items); denom=n+e; r=rem
        for c,v in items: out[c]=out.get(c,0.0)+r*v/denom
        rem=r*e/denom
        excl.update(c for c,_ in items)
        if rem<1e-12: break
    left=[c for c in A if c not in excl]
    if left:
        u=rem/len(left)
        for c in left: out[c]=out.get(c,0.0)+u
    return out

def probs(text,K,esc):
    return np.array([dist(text[:i],K,esc).get(text[i],1e-9) for i in range(len(text))])

def em(P,iters=300):
    w=np.ones(P.shape[1])/P.shape[1]
    for _ in range(iters):
        r=P*w; s=r.sum(1,keepdims=True); r=r/s
        w=r.mean(0)
    return w

for name,sl in (("tune",val[20000:30000]),):
    P=np.column_stack([probs(sl,K,0.8) for K in KS])
    for i,K in enumerate(KS):
        print(f"K={K} alone bpc={-np.log2(P[:,i]).mean():.5f}",flush=True)
    w=em(P)
    print("weights",dict(zip(KS,np.round(w,4))),flush=True)
    print("mix bpc tune =",-np.log2(P@w).mean(),flush=True)
    # check on holdout slices
    for nm,sl2 in (("evalval",val[:8000]),("evaltest",val[55770:63770]),("tune2",val[40000:50000])):
        P2=np.column_stack([probs(sl2,K,0.8) for K in KS])
        print(nm,"mix=",-np.log2(P2@w).mean()," bestsingleK5=",-np.log2(P2[:,KS.index(5)]).mean(),flush=True)
    np.save(S+"/w.npy",w)
