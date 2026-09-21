// Floating-point block-weight descent for a fixed template (heuristic only;
// the result is rounded to integers and re-scored EXACTLY by hill/eval.py).
// usage: wopt in.rows out.weights iters scale [init.weights]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#define N 768
#define W 12
typedef uint64_t u64;
static u64 A[2][N][W];static char row[N+8];static double w[N],g[N],wn[N],g2[N];
static double grad(const double*w,double*g){ // returns P (sum w = 1)
  double P=0;for(int i=0;i<N;i++){double s=0;for(int c=0;c<2;c++){u64*Ni=A[c][i];
    for(int kb=0;kb<W;kb++){u64 mb=Ni[kb];while(mb){int b=kb*64+__builtin_ctzll(mb);mb&=mb-1;
      u64 Cb[W];for(int q=0;q<W;q++)Cb[q]=Ni[q]&A[c][b][q];double sb=0;
      for(int kc=0;kc<W;kc++){u64 mc=Cb[kc];while(mc){int cc=kc*64+__builtin_ctzll(mc);mc&=mc-1;double sd=0;
        for(int q=0;q<W;q++){u64 md=Cb[q]&A[c][cc][q];while(md){sd+=w[q*64+__builtin_ctzll(md)];md&=md-1;}}
        sb+=w[cc]*sd;}}
      s+=w[b]*sb;}}}
    g[i]=4*s;P+=w[i]*s;}return P;}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");int iters=atoi(argv[3]);int scale=atoi(argv[4]);
  for(int a=0;a<N;a++){fscanf(f,"%s",row);for(int b=0;b<N;b++){int c=(row[b]=='1')?0:1; if(a!=b||c==1)A[c][a][b>>6]|=1ULL<<(b&63);}}
  for(int i=0;i<N;i++)w[i]=1.0/N;
  if(argc>5){FILE*h=fopen(argv[5],"r");double s=0;for(int i=0;i<N;i++){fscanf(h,"%lf",&w[i]);s+=w[i];}for(int i=0;i<N;i++)w[i]/=s;fclose(h);}
  double P=grad(w,g);printf("P0=%.15f\n",P);
  double gm=0,gv=0;for(int i=0;i<N;i++)gm+=g[i]/N;for(int i=0;i<N;i++)gv+=(g[i]-gm)*(g[i]-gm)/N;printf("grad mean %.6e sd %.6e\n",gm,sqrt(gv));
  double eta=1e-3/ (sqrt(gv)+1e-30) /N;
  for(int it=0;it<iters;it++){gm=0;for(int i=0;i<N;i++)gm+=g[i]/N;
    int ok=0;for(int tr=0;tr<12;tr++){double s=0;for(int i=0;i<N;i++){wn[i]=w[i]-eta*(g[i]-gm);if(wn[i]<1e-6/N)wn[i]=1e-6/N;s+=wn[i];}
      for(int i=0;i<N;i++)wn[i]/=s;double P2=grad(wn,g2);
      if(P2<P){P=P2;memcpy(w,wn,sizeof w);memcpy(g,g2,sizeof g);eta*=2;ok=1;break;}eta/=3;}
    printf("it %d P=%.15f eta=%g\n",it,P,eta);fflush(stdout);if(!ok)break;
    FILE*o=fopen(argv[2],"w");for(int i=0;i<N;i++)fprintf(o,"%ld\n",lround(w[i]*N*scale));fclose(o);}
  return 0;}
