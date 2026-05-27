import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse
import json
import numpy as np
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=False,
    allow_headers=["*"],
    expose_headers=["*"]
)
class Payload(BaseModel):
    regions: List[str]
    threshold_ms: int

@app.post("/api/latency")
async def analyze(payload:Payload):
    with open('q-vercel-latency.json') as file:
        data=json.load(file)
    result={'regions':{}}
    for region in payload.regions:
        count=0
        uptimes=[]
        latencies=[]
        for i in range(len(data)):
            if(data[i]["region"]==region):
                uptimes.append(data[i]["uptime_pct"])
                latencies.append(data[i]["latency_ms"])
                if(data[i]["latency_ms"]>payload.threshold_ms):
                    count+=1
            else:
                continue
        if not latencies:
            result['regions'][region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        avg_latency=sum(latencies)/len(latencies)
        p95_latency = np.percentile(latencies,95)
        avg_uptime= sum(uptimes)/len(uptimes)
        result['regions'][region]={
        'avg_latency':round(avg_latency,2),
        'p95_latency':round(p95_latency,2),
        'avg_uptime':round(avg_uptime,3),
        'breaches':count
        }
    #     response = JSONResponse(content=result)

    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Methods"] = "*"
    # response.headers["Access-Control-Allow-Headers"] = "*"

    return result


       