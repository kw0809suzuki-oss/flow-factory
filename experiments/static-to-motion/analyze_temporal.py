#!/usr/bin/env python3
import json
with open("temporal_observations.json",encoding="utf-8") as f:
    d=json.load(f)
stable={k:v for k,v in d["stable_relations"].items() if v["present"]==v["total"]}
print(json.dumps({
 "frames":d["frames"],
 "stable_relation_count":len(stable),
 "stable_relations":list(stable),
 "transformed_over_time":d["transformed_over_time"],
 "boundary":d["boundary"]
},ensure_ascii=False,indent=2))
