"""Recalcula, solo lectura, las métricas de las corridas N=50 contra final_is_error.

Uso: python3 -I eval_final_gt.py <scripts_dir>
Alinea por posición del batch (batch k del SLM == batch k del GT, verificado por entry_count y
por same_batch_top1_rate=1.0 en los reports de la matriz).
"""
import json, os, sys, glob, collections
base = sys.argv[1]
gt_path = os.path.join(base, 'pseudo_labeling/data/batches_n50/ground_truth_final/ground_truth_batches_final.jsonl')
gt = [json.loads(l) for l in open(gt_path)]
gt.sort(key=lambda r: r['batch_id'] if isinstance(r['batch_id'], int) else int(str(r['batch_id']).split('_')[-1]))
print('GT rows', len(gt), 'positives', sum(int(r['final_is_error']) for r in gt), 'first keys', list(gt[0].keys())[:8], 'batch_id sample', gt[0]['batch_id'], gt[-1]['batch_id'])
y_gt = {}
for i, r in enumerate(gt):
    y_gt[i] = int(r['final_is_error'])
cons = {i: int(r['consensus_is_error']) for i, r in enumerate(gt)}

def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return None
    pairs = sorted([(s, l) for s, l in zip(scores, labels)])
    # rank-based AUC with ties
    ranks = {}
    i = 0
    vals = [s for s, _ in pairs]
    n = len(vals)
    r = [0.0] * n
    while i < n:
        j = i
        while j + 1 < n and vals[j + 1] == vals[i]:
            j += 1
        for k in range(i, j + 1):
            r[k] = (i + j) / 2 + 1
        i = j + 1
    sum_pos = sum(rk for rk, (_, l) in zip(r, pairs) if l == 1)
    return (sum_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))

for d in sorted(glob.glob(os.path.join(base, 'analysis/batch_size_matrix/n50/*'))):
    f = os.path.join(d, 'log_analysis.jsonl')
    if not os.path.exists(f):
        continue
    recs = [json.loads(l) for l in open(f)]
    byrun = collections.defaultdict(list)
    for r in recs:
        byrun[r.get('run_id')].append(r)
    run = max(byrun.values(), key=len)
    tp = fp = tn = fn = inval = 0
    sc, lab = [], []
    tp_c = fp_c = tn_c = fn_c = 0
    for k, r in enumerate(run):
        bid = r.get('batch_id')
        idx = bid if isinstance(bid, int) else k
        if idx not in y_gt:
            continue
        if not r.get('is_valid_response', True):
            inval += 1
            continue
        p = 1 if r.get('error_found') else 0
        y = y_gt[idx]
        tp += p and y; fp += p and not y; fn += (not p) and y; tn += (not p) and (not y)
        if r.get('error_probability') is not None:
            sc.append(r['error_probability']); lab.append(y)
    n = tp + fp + tn + fn
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    print(os.path.basename(d), 'runs', {k: len(v) for k, v in byrun.items()}, 'valid', n, 'invalid', inval,
          'acc %.3f prec %.3f rec %.3f f1 %.3f spec %.3f' % ((tp + tn) / n, prec, rec, f1, tn / (tn + fp) if tn + fp else 0),
          'TP', tp, 'FP', fp, 'TN', tn, 'FN', fn, 'auc', None if auc(sc, lab) is None else round(auc(sc, lab), 3), 'n_scored', len(sc),
          'predpos', tp + fp)
