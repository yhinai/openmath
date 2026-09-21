// Tabu edge-flip local search for the K4 blow-up objective (uniform weights,
// all-blue diagonal).  T = red + blue ordered monochromatic 4-tuples; density = T/n^4.
// usage: tabu in.rows out.rows seed tenure seconds
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#define N 768
#define W 12
typedef uint64_t u64;
static u64 R[N][W], B[N][W];
static int32_t er[N][N], eb[N][N];
static int tabu[N][N];
static u64 BR[N][W];
static char row[N+8];
static inline int has(u64*m,int i){return (m[i>>6]>>(i&63))&1;}
static inline void flipbit(u64*m,int i){m[i>>6]^=1ULL<<(i&63);}
static int ecount(u64 A[N][W],int a,int b,int*csz){
  u64 C[W];int c=0,e=0;
  for(int k=0;k<W;k++){C[k]=A[a][k]&A[b][k];c+=__builtin_popcountll(C[k]);}
  for(int k=0;k<W;k++){u64 m=C[k];while(m){int x=k*64+__builtin_ctzll(m);m&=m-1;
    for(int q=0;q<W;q++)e+=__builtin_popcountll(A[x][q]&C[q]);}}
  if(csz)*csz=c;return e/2;}
static inline int csize(u64 A[N][W],int a,int b){int c=0;for(int k=0;k<W;k++)c+=__builtin_popcountll(A[a][k]&A[b][k]);return c;}
static inline long gain(int a,int b){ // change in T if pair flipped
  long db=24L*eb[a][b]+36L*csize(B,a,b)+14, dr=24L*er[a][b];
  return has(R[a],b)? db-dr : dr-db;}
static long total(void){long t=N;for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){
  if(has(R[a],b))t+=4L*er[a][b];else t+=4L*eb[a][b]+12L*csize(B,a,b)+14;}return t;}
static void recompute_vertex(int u){for(int b=0;b<N;b++)if(b!=u){
  er[u][b]=er[b][u]=ecount(R,u,b,0);eb[u][b]=eb[b][u]=ecount(B,u,b,0);}}
static void doflip(int u,int v){
  u64 C[W];int lst[N],n=0;int wasred=has(R[u],v);
  u64 (*A)[W]=wasred?R:B;int32_t (*e)[N]=wasred?er:eb;
  for(int k=0;k<W;k++){C[k]=A[u][k]&A[v][k];u64 m=C[k];while(m){lst[n++]=k*64+__builtin_ctzll(m);m&=m-1;}}
  for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){e[lst[i]][lst[j]]--;e[lst[j]][lst[i]]--;}
  flipbit(R[u],v);flipbit(R[v],u);flipbit(B[u],v);flipbit(B[v],u);
  A=wasred?B:R;e=wasred?eb:er;n=0;
  for(int k=0;k<W;k++){C[k]=A[u][k]&A[v][k];u64 m=C[k];while(m){lst[n++]=k*64+__builtin_ctzll(m);m&=m-1;}}
  for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){e[lst[i]][lst[j]]++;e[lst[j]][lst[i]]++;}
  recompute_vertex(u);recompute_vertex(v);}
static void save(const char*fn){char tmp[1024];snprintf(tmp,1024,"%s.tmp",fn);FILE*f=fopen(tmp,"w");
  for(int a=0;a<N;a++){for(int b=0;b<N;b++)row[b]=has(BR[a],b)?'1':'0';row[N]=0;fprintf(f,"%s\n",row);}fclose(f);rename(tmp,fn);}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r");srand(atoi(argv[3]));int ten=atoi(argv[4]);double secs=atof(argv[5]);
  for(int a=0;a<N;a++){if(fscanf(f,"%s",row)!=1)return 1;for(int b=0;b<N;b++)if(a!=b){if(row[b]=='1')flipbit(R[a],b);else flipbit(B[a],b);}}
  fclose(f);
  for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){er[a][b]=er[b][a]=ecount(R,a,b,0);eb[a][b]=eb[b][a]=ecount(B,a,b,0);}
  long T=total(),best=T;printf("start T=%ld\n",T);fflush(stdout);
  time_t t0=time(0);long it=0;
  while(difftime(time(0),t0)<secs){it++;
    long bg=1L<<60;int bu=-1,bv=-1,ties=0;
    for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){long g=gain(a,b);
      if(tabu[a][b]>it && T+g>=best)continue;
      if(g<bg){bg=g;bu=a;bv=b;ties=1;}else if(g==bg&&rand()%(++ties)==0){bu=a;bv=b;}}
    if(bu<0)continue;
    doflip(bu,bv);T+=bg;tabu[bu][bv]=it+ten+rand()%(ten+1);
    if(T<best){best=T;memcpy(BR,R,sizeof R);}
    if(it%5000==0){long chk=total();printf("it=%ld T=%ld best=%ld chk=%s\n",it,T,best,chk==T?"ok":"MISMATCH");fflush(stdout);if(chk!=T)return 2;}
    static long saved=1L<<60;static time_t ls=0;
    if(best<saved&&difftime(time(0),ls)>=5){save(argv[2]);saved=best;ls=time(0);printf("saved %ld\n",best);fflush(stdout);}
  }
  save(argv[2]);printf("done best=%ld it=%ld\n",best,it);return 0;}
