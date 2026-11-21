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

parameters = json.load(open(sys.argv[1], encoding="utf-8"))
rows = list(csv.DictReader(open(parameters["observations"], encoding="utf-8")))
os.makedirs("results", exist_ok=True)
with open(os.path.join("results", "means.csv"), "w", encoding="utf-8") as out:
    out.write("station,mean_c\n")
    for station in parameters["stations"]:
        values = [float(r["temperature_c"]) for r in rows if r["station"] == station]
        out.write("%s,%.2f\n" % (station, sum(values) / len(values)))
