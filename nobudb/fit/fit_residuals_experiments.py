import numpy as np, re, sys
from scipy.optimize import least_squares
src=open('nobudb/fit/fit_damage.py',encoding='utf8').read()
pre=src.split('names = [d[0]')[0]
exec(pre)
names=[d[0] for d in D]
T=np.array([d[1] for d in D]);A=np.array([d[2] for d in D]);Dd=np.array([d[3] for d in D]);ks=[d[5] for d in D];act=np.array([d[6] for d in D],float)
# M 重新拆：把可疑項抽成旗標
Mb=np.array([d[4] for d in D])
tag=lambda s:np.array([1.0 if s in n else 0.0 for n in names])
crit=tag('會心'); qi=tag('氣勢'); shen=tag('深謀'); fu=tag('疾風'); lei=tag('雷鳴'); rifi=tag('理非'); ren=tag('連擊')
# 還原已含在 M 裡的項目，改成可調參數
base=Mb/ (np.where(crit>0,1.525,1)*np.where(qi>0,(1-0.3506),1)*np.where(shen>0,(1-0.2681),1)*np.where(fu>0,0.76,1)*np.where(lei>0,0.62,1)*np.where(rifi>0,1.92,1))
kind=np.array([{"none":0,"adv":1,"dis":2}[k] for k in ks])
def model(p,free):
    c,a,s,q,adv,dis=p[:6]; i=6
    g=c*1e-3*T**q*(A+a)*np.exp(-Dd/s)*(10000**(1-q))
    g=g*np.where(kind==1,adv,np.where(kind==2,dis,1))
    f={}
    for k in free: f[k]=p[i];i+=1
    mult=base.copy()
    mult=mult*np.where(crit>0,f.get('crit',1.525),1)*np.where(qi>0,1-f.get('qi',.3506),1)*np.where(shen>0,1-f.get('shen',.2681),1)*np.where(fu>0,f.get('fu',.76),1)*np.where(lei>0,f.get('lei',.62),1)*np.where(rifi>0,f.get('rifi',1.92),1)
    return g*mult
init={'crit':1.525,'qi':.3506,'shen':.2681,'fu':.76,'lei':.62,'rifi':1.92}
for free in [[],['crit'],['qi'],['fu'],['crit','qi'],['crit','qi','shen'],['crit','qi','shen','fu','lei']]:
    p0=[.339,136.6,224.2,.665,1.224,.956]+[init[k] for k in free]
    r=least_squares(lambda p:model(p,free)/act-1,p0,max_nfev=20000)
    e=r.fun
    print(free,'rms %.1f%% max %.1f%% 5%%內 %d/32'%(np.sqrt(np.mean(e**2))*100,np.max(abs(e))*100,np.sum(abs(e)<=.05)),np.round(r.x,3))

print('--- LOO 交叉驗證（每次拿掉 1 筆，預測它）')
def loo(free,fixq=None):
    errs=[]
    n=len(D)
    for i in range(n):
        m=np.ones(n,bool);m[i]=False
        p0=[.339,136.6,224.2,.665,1.224,.956]+[init[k] for k in free]
        def res(p):
            return (model(p,free)/act-1)[m]
        r=least_squares(res,p0,max_nfev=5000)
        errs.append(model(r.x,free)[i]/act[i]-1)
    e=np.array(errs);return np.sqrt(np.mean(e**2))*100,np.sum(abs(e)<=.05)
for free in [[],['crit'],['qi'],['crit','qi'],['crit','qi','shen']]:
    print(free,'LOO rms %.1f%% 5%%內 %d/32'%loo(free))
