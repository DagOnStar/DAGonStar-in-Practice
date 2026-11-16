"""Importable functions used by the native (Python) tasks of the course.

A native task names a function as "module:function"; DAGonStar imports it in
a separate Python process inside the task's working directory, binds files
and values to its parameters and stores its return value as JSON.
"""
import csv
import json
import os
import statistics


def _rows(observations):
    with open(observations, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def mean_temperature(observations, result):
    """Mean temperature of every record; returns the number of records."""
    values = [float(row["temperature_c"]) for row in _rows(observations)]
    with open(result, "w", encoding="utf-8") as stream:
        json.dump({"mean_temperature_c": round(sum(values) / len(values), 2)}, stream, sort_keys=True)
    return {"count": len(values)}


def station_summary(observations, station, summary):
    """Mean temperature and maximum wind of one station."""
    rows = [row for row in _rows(observations) if row["station"] == station]
    if not rows:
        raise ValueError("no records for station %s" % station)
    data = {"station": station,
            "mean_temperature_c": round(statistics.mean(float(r["temperature_c"]) for r in rows), 2),
            "max_wind_m_s": max(float(r["wind_m_s"]) for r in rows),
            "records": len(rows)}
    with open(summary, "w", encoding="utf-8") as stream:
        json.dump(data, stream, sort_keys=True)
    return data


def merge_summaries(nap, cap, isc, report):
    """Fan-in: merge three station summaries into one report."""
    stations = []
    for path in (nap, cap, isc):
        with open(path, encoding="utf-8") as stream:
            stations.append(json.load(stream))
    windiest = max(stations, key=lambda s: s["max_wind_m_s"])
    data = {"stations": sorted(s["station"] for s in stations), "windiest": windiest["station"],
            "max_wind_m_s": windiest["max_wind_m_s"]}
    with open(report, "w", encoding="utf-8") as stream:
        json.dump(data, stream, sort_keys=True)
    return data


def scale_wind(observations, factor, unit, scaled):
    """Scalar inputs: multiply wind speeds by *factor* and label them with *unit*."""
    rows = _rows(observations)
    with open(scaled, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["station", "time_utc", "wind_" + unit])
        for row in rows:
            writer.writerow([row["station"], row["time_utc"], round(float(row["wind_m_s"]) * factor, 2)])
    return {"factor": factor, "unit": unit, "rows": len(rows), "label": os.environ.get("COURSE_LABEL", "unset")}


def ensemble_member(observations, offset, member):
    """One ensemble member: perturb every temperature by *offset* and return the mean."""
    values = [float(row["temperature_c"]) + offset for row in _rows(observations)]
    mean = round(sum(values) / len(values), 3)
    with open(member, "w", encoding="utf-8") as stream:
        json.dump({"offset": offset, "mean_temperature_c": mean}, stream, sort_keys=True)
    return {"mean_temperature_c": mean}


def ensemble_statistics(m0, m1, m2, m3, m4, statistics_file):
    """Fan-in over five members: ensemble mean and spread."""
    means = []
    for path in (m0, m1, m2, m3, m4):
        with open(path, encoding="utf-8") as stream:
            means.append(json.load(stream)["mean_temperature_c"])
    data = {"members": len(means), "ensemble_mean_c": round(statistics.mean(means), 3),
            "spread_c": round(statistics.pstdev(means), 3)}
    with open(statistics_file, "w", encoding="utf-8") as stream:
        json.dump(data, stream, sort_keys=True)
    return data


def always_fails(observations):
    """Used by the failure lecture: a native function that raises."""
    raise RuntimeError("calibration table missing for %s" % os.path.basename(observations))


def events_to_observations(input_file, output_file):
    """Normalise an IoT observation envelope into a record table."""
    with open(input_file, encoding="utf-8") as source:
        events = json.load(source)["events"]
    keys = ("id", "station", "temperature_c")
    records = [{key: event[key] for key in keys if key in event} for event in events]
    with open(output_file, "w", encoding="utf-8") as destination:
        json.dump({"observations": records}, destination, sort_keys=True)
    return {"count": len(records)}


def count_records(input_file, output_file):
    """Count the records of a JSON table."""
    with open(input_file, encoding="utf-8") as source:
        records = json.load(source)["observations"]
    with open(output_file, "w", encoding="utf-8") as destination:
        json.dump({"count": len(records)}, destination)
    return {"count": len(records)}
