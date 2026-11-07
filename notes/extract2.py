import json, glob, sys, os
base = sys.argv[1]
files = sorted(glob.glob(os.path.join(base, 'analysis', '*', '*', 'eval_report.json')))
first = True
for f in files:
    d = json.load(open(f))
    if first:
        print('keys:', list(d.keys()))
        first = False
    rel = os.path.relpath(f, base)
    flat = {}
    def walk(x, p=''):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('roc_curve',):
                    continue
                walk(v, p + k + '.')
        elif isinstance(x, (int, float, str)) or x is None:
            flat[p[:-1]] = x
    walk(d)
    keep = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in flat.items()
            if any(s in k for s in ('accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'batches', 'total', 'positives', 'ref_key', 'unclassified'))}
    print(rel, keep)
