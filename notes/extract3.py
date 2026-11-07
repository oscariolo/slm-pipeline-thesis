import json, glob, sys, os
base = sys.argv[1]
for f in sorted(glob.glob(os.path.join(base, 'comparison', '*', 'report.json'))):
    d = json.load(open(f))
    m = d['model']
    print(m['model_name'][-34:], m['batch_size'], 'top1same=', d.get('same_batch_top1_rate'),
          'overlap=', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in (d.get('index_overlap') or {}).items() if not isinstance(v, (list, dict))},
          'agree=', d.get('knn_vs_overlap_agreement'),
          'sim=', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in (d.get('similarity') or {}).items() if not isinstance(v, (list, dict))})
