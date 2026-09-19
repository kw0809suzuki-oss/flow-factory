#!/usr/bin/env python3
import json
from collections import Counter

with open("observations.json",encoding="utf-8") as f:
    d=json.load(f)
samples=d["samples"]
keys=list(samples[0]["features"])
pres={}
for k in keys:
    n=sum(1 for s in samples if s["features"].get(k) is True)
    pres[k]={"present":n,"total":len(samples),"fraction":n/len(samples)}
stable=[k for k,v in pres.items() if v["fraction"]==1.0]
changed_fields={}
for field in ["framing","pose","text_layer"]:
    vals=[s["changed"][field] for s in samples]
    changed_fields[field]={"distinct_values":len(set(map(str,vals))),"values":vals}
print(json.dumps({
 "samples":len(samples),
 "preservation":pres,
 "stable_relations":stable,
 "transformed_dimensions":changed_fields,
 "boundary":d["boundary"]
},ensure_ascii=False,indent=2))
