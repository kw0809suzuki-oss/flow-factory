#!/usr/bin/env python3
import argparse, csv, json, math, random
from collections import Counter
from itertools import combinations

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    return [sorted([int(r[f"n{i}"]) for i in range(1,7)]) for r in rows]

def metrics(draws):
    n=len(draws)
    gap_sigs=[]
    largest_holes=[]
    mirror=[]
    mod3_peak=[]
    overlap=[]
    near1=[]
    near2=[]
    rank_motion=[]
    pair_memory=[]
    seen_pairs=[]
    for i,d in enumerate(draws):
        gaps=[d[j+1]-d[j] for j in range(5)]
        gap_sigs.append(tuple(gaps))
        circular=gaps+[43-d[-1]+d[0]]
        largest_holes.append(max(circular)-1)
        s=set(d)
        mirror.append(sum(1 for x in d if 44-x in s and x < 44-x))
        c=Counter(x%3 for x in d)
        mod3_peak.append(max(c.values()))
        if i:
            prev=set(draws[i-1])
            overlap.append(len(s & prev))
            near1.append(sum(1 for x in d if any(abs(x-y)<=1 for y in prev)))
            near2.append(sum(1 for x in d if any(abs(x-y)<=2 for y in prev)))
            rank_motion.append(sum(abs(d[j]-draws[i-1][j]) for j in range(6))/6)
        pairs=set(combinations(d,2))
        if i:
            recent=set().union(*seen_pairs[max(0,i-10):]) if seen_pairs[max(0,i-10):] else set()
            pair_memory.append(len(pairs & recent))
        seen_pairs.append(pairs)
    sig_counts=Counter(gap_sigs)
    repeated_gap_draws=sum(v for v in sig_counts.values() if v>1)
    return {
        "repeated_gap_draw_fraction": repeated_gap_draws/n,
        "largest_hole_mean": sum(largest_holes)/n,
        "mirror_pairs_mean": sum(mirror)/n,
        "mod3_peak_mean": sum(mod3_peak)/n,
        "carry_overlap_mean": sum(overlap)/len(overlap),
        "carry_near1_mean": sum(near1)/len(near1),
        "carry_near2_mean": sum(near2)/len(near2),
        "rank_motion_abs_mean": sum(rank_motion)/len(rank_motion),
        "pair_memory_10_mean": sum(pair_memory)/len(pair_memory),
    }

def random_draws(rng,n):
    return [sorted(rng.sample(range(1,44),6)) for _ in range(n)]

def empirical(real, controls):
    out={}
    for k,v in real.items():
        vals=[m[k] for m in controls]
        mean=sum(vals)/len(vals)
        sd=(sum((x-mean)**2 for x in vals)/(len(vals)-1))**0.5 if len(vals)>1 else 0.0
        lower=(sum(x<=v for x in vals)+1)/(len(vals)+1)
        upper=(sum(x>=v for x in vals)+1)/(len(vals)+1)
        p2=min(1.0,2*min(lower,upper))
        out[k]={
            "real":v,
            "control_mean":mean,
            "control_sd":sd,
            "z": None if sd==0 else (v-mean)/sd,
            "empirical_two_sided_p":p2,
            "control_min":min(vals),
            "control_max":max(vals),
        }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",default="data.csv")
    ap.add_argument("--controls",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=20260919)
    args=ap.parse_args()
    draws=load(args.data)
    rng=random.Random(args.seed)
    real=metrics(draws)
    controls=[metrics(random_draws(rng,len(draws))) for _ in range(args.controls)]
    comparison=empirical(real,controls)
    interesting={k:v for k,v in comparison.items() if v["empirical_two_sided_p"] <= 0.05}
    print(json.dumps({
        "draws":len(draws),
        "controls":args.controls,
        "seed":args.seed,
        "comparison":comparison,
        "interesting_at_p_le_0_05":interesting,
        "boundary":"Post-hoc metrics on 100 historical draws. Exploratory only; no prediction claim. Multiple comparisons are not corrected in this first pass."
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
