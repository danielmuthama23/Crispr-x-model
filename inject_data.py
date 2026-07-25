#!/usr/bin/env python3
"""
inject_data.py
---------------
Reads synthetic data as JSON on stdin (from generate_synthetic_data.py) and
splices it directly into crispr-x.html's COMPOUND_DB and initial cohort
JS arrays, replacing the hand-typed values with the piped-in data.
Writes the resulting HTML to stdout.

Usage:
    python3 generate_synthetic_data.py | python3 inject_data.py crispr-x.html > crispr-x-generated.html
"""
import json
import re
import sys


def js_bool(b):
    return "true" if b else "false"


def render_compound_db(compounds):
    lines = ["const COMPOUND_DB = ["]
    for c in compounds:
        tags = ",".join(f'"{t}"' for t in c["tags"])
        lines.append(
            f'  {{ name:"{c["name"]}", smiles:"{c["smiles"]}", '
            f'mw:{c["mw"]}, logp:{c["logp"]}, hbd:{c["hbd"]}, hba:{c["hba"]}, '
            f'tpsa:{c["tpsa"]}, rotb:{c["rotb"]}, tags:[{tags}] }},'
        )
    lines.append("];")
    return "\n".join(lines)


def render_cohort(cohort):
    entries = []
    for p in cohort:
        entries.append(
            f'{{ id:"{p["id"]}", age:{p["age"]}, sex:"{p["sex"]}", '
            f'consented:{js_bool(p["consented"])}, dose:"{p["dose"]}", ae:[] }}'
        )
    return "[\n  " + ",\n  ".join(entries) + "\n]"


def main():
    if len(sys.argv) != 2:
        print("usage: generate_synthetic_data.py | inject_data.py <html-file> > out.html", file=sys.stderr)
        sys.exit(1)

    html_path = sys.argv[1]
    payload = json.load(sys.stdin)

    html = open(html_path, encoding="utf-8").read()

    # --- 1. replace COMPOUND_DB block ---
    compound_pattern = re.compile(
        r"const COMPOUND_DB = \[.*?\n\];", re.S
    )
    new_compound_block = render_compound_db(payload["compounds"])
    html, n1 = compound_pattern.subn(new_compound_block, html, count=1)
    if n1 != 1:
        print("WARNING: COMPOUND_DB block not found/replaced", file=sys.stderr)

    # --- 2. replace initial cohort seed + patientCounter ---
    cohort_json = render_cohort(payload["cohort"])
    next_counter = len(payload["cohort"]) + 1
    cohort_pattern = re.compile(
        r"let cohort = \[\]; // \{id, age, sex, consented, dose, ae:\[\]\}\nlet patientCounter = 1;"
    )
    replacement = (
        f"let cohort = {cohort_json}; // seeded from piped synthetic data ({payload['meta']['generator']}, seed {payload['meta']['seed']})\n"
        f"let patientCounter = {next_counter};"
    )
    html, n2 = cohort_pattern.subn(replacement, html, count=1)
    if n2 != 1:
        print("WARNING: cohort init block not found/replaced", file=sys.stderr)

    # --- 3. add a small provenance comment near the top of the script ---
    provenance = (
        f"\n// --- synthetic data injected via pipe: {payload['meta']['generator']} "
        f"(seed={payload['meta']['seed']}) — not hand-typed. See README for the pipe command. ---\n"
    )
    html = html.replace("<script>\n", "<script>" + provenance, 1)

    sys.stdout.write(html)
    print(f"Injected {len(payload['compounds'])} compounds and {len(payload['cohort'])} cohort patients "
          f"into {html_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
