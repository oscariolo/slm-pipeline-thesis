import json, glob, sys, os
base = sys.argv[1]
files = sorted(glob.glob(os.path.join(base, 'comparison', '*', 'report.json')))
print('keys:', list(json.load(open(files[0])).keys()))
rows = []
for f in files:
    d = json.load(open(f))
    m = d['model']
    k = d.get('knn', {})
    o = d.get('overlap', {}) or {}
    rows.append((m['model_name'], m['batch_size'], d['batches'], d['reference']['label_key'],
                 k.get('accuracy'), k.get('precision'), k.get('recall'), k.get('f1_score'),
                 k.get('specificity'), k.get('matthews_corrcoef'), k.get('roc_auc'),
                 k.get('positives_reference'), k.get('positives_predicted'), k.get('confusion_matrix'),
                 o.get('f1_score'), o.get('accuracy')))
rows.sort(key=lambda r: (r[1] != 50, r[1], -(r[7] or 0)))
for r in rows:
    print(' | '.join(str(round(x, 3)) if isinstance(x, float) else str(x) for x in r))
