"""A stand-in for an external workflow engine: it knows nothing about DAGonStar.

    python station_engine.py PARAMETERS.json

It reads the JSON parameter document that DAGonStar's generic ``command`` adapter
writes, computes the mean temperature of each requested station from the CSV named
by ``observations``, and writes results/means.csv in its working directory.
"""
import csv
import json
import os
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    parameters = json.load(f)
with open(parameters["observations"], encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
os.makedirs("results", exist_ok=True)
with open("results/means.csv", "w", encoding="utf-8") as out:
    out.write("station,mean_c\n")
    for station in parameters["stations"]:
        values = [float(r["temperature_c"])
                  for r in rows if r["station"] == station]
        mean = sum(values) / len(values)
        out.write("%s,%.2f\n" % (station, mean))
