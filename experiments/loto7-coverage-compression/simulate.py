import random, math, statistics, json
from collections import defaultdict

N=37
WIN=7
TICKETS=10
PICKS=7
TRIALS=4000
SEED=20260919
random.seed(SEED)

POOL_SIZES=[8,10,12,15,18,22,26,30,37]
STRENGTHS=[0.0,0.25,0.5,0.75,1.0,1.5,2.0,3.0]

def one_trial(strength,pool_size):
    winners=set(random.sample(range(1,N+1),WIN))
    scored=[]
    for n in range(1,N+1):
        score=random.gauss(0,1)+(strength if n in winners else 0)
        scored.append((score,n))
    scored.sort(reverse=True)
    pool=[n for _,n in scored[:pool_size]]

    ranks={n:i for i,n in enumerate(pool)}
    tickets=[]
    usage=defaultdict(int)
    for _ in range(TICKETS):
        weights=[]
        avail=pool[:]
        for n in avail:
            rank_weight=math.exp(-ranks[n]/max(3,pool_size/4))
            diversity_penalty=1/(1+usage[n]*0.65)
            weights.append(rank_weight*diversity_penalty)
        chosen=[]
        for _j in range(PICKS):
            total=sum(weights)
            r=random.random()*total
            acc=0
            idx=0
            for i,w in enumerate(weights):
                acc+=w
                if acc>=r:
                    idx=i; break
            n=avail.pop(idx); weights.pop(idx)
            chosen.append(n); usage[n]+=1
        tickets.append(set(chosen))

    hits=[len(t&winners) for t in tickets]
    unique=len(set().union(*tickets))
    pool_hits=len(set(pool)&winners)
    return {
        'max_hit':max(hits),
        'mean_hit':sum(hits)/len(hits),
        'hit4plus':int(max(hits)>=4),
        'hit5plus':int(max(hits)>=5),
        'hit6plus':int(max(hits)>=6),
        'pool_hits':pool_hits,
        'unique_used':unique,
    }

rows=[]
for s in STRENGTHS:
    for p in POOL_SIZES:
        vals=[one_trial(s,p) for _ in range(TRIALS)]
        rows.append({
            'strength':s,
            'pool_size':p,
            'coverage_pct':round(p/N*100,1),
            'avg_unique_used':round(statistics.mean(v['unique_used'] for v in vals),2),
            'avg_pool_hits':round(statistics.mean(v['pool_hits'] for v in vals),3),
            'avg_max_hit':round(statistics.mean(v['max_hit'] for v in vals),4),
            'p4plus':round(statistics.mean(v['hit4plus'] for v in vals),4),
            'p5plus':round(statistics.mean(v['hit5plus'] for v in vals),4),
            'p6plus':round(statistics.mean(v['hit6plus'] for v in vals),4),
        })

best={}
for s in STRENGTHS:
    rs=[r for r in rows if r['strength']==s]
    best[s]=max(rs,key=lambda r:(r['p5plus'],r['avg_max_hit']))

out={'seed':SEED,'trials_per_cell':TRIALS,'rows':rows,'best_by_strength':best,
     'boundary':'Synthetic signal-strength experiment only. It does not estimate real LOTO7 model skill or future win probability.'}
print(json.dumps(out,ensure_ascii=False,indent=2))
