# Phase 8 — Tourist Behaviour Analysis: Status

## What it does
Groups 1,000 synthetic tourists by movement pattern using DBSCAN
(unsupervised — no labels used during clustering). Tourists who don't fit
any dense cluster are flagged as outliers.

## Pipeline
1. `build_tourist_features.py` — turns 13,553 raw visit-events into
   1,000 tourist-level behaviour features (visits, unique clusters
   visited, restricted-zone ratio, dwell time, distance, revisit ratio)
2. `train_behaviour_dbscan.py` — scales features, runs DBSCAN
   (eps=1.2, min_samples=8 — chosen by inspection, not learned; DBSCAN
   has no training phase), outputs cluster assignments

## Result
- 4 normal-behaviour clusters found, 177 tourists (17.7%) flagged as outliers

## Validation — read this carefully
Per the Phase 0 decision, unsupervised modules don't get
accuracy/precision/recall — there's no real ground truth. What we CAN
check: does DBSCAN's outlier flag line up with the `is_suspicious_tourist`
flag we deliberately injected into the synthetic data generator?

- **70.8% capture rate**: of the 65 tourists we synthetically marked
  suspicious, DBSCAN's outlier detection caught 46 of them
- **4.0x lift over random chance**: outliers are ~4x more likely to be
  "suspicious" than a random tourist

**What this proves and doesn't prove:** it confirms the clustering
pipeline correctly picks up on unusual movement patterns *as we defined
them in the synthetic generator*. It does NOT prove the model would catch
real suspicious tourists — that depends entirely on whether our synthetic
definition of "suspicious" (elevated restricted-zone visits) matches real
suspicious behaviour, which is untested. Say this plainly in any demo.

## Known limitations
- eps/min_samples were chosen by trying values and inspecting cluster
  counts, not via a principled tuning process (e.g. k-distance elbow
  plot) — worth doing properly before this goes further
- 29.2% of injected-suspicious tourists were NOT caught (missed) —
  worth investigating which ones, and why, before trusting this in Phase 10
- Feature set is deliberately simple (8 features) — could be extended
  with time-of-day patterns, sequence-based features, etc.

## Next
Phase 9 — Suspicious Movement Detection (Isolation Forest) can reuse
`tourist_behaviour_features.csv` directly — same feature table, different
algorithm, useful to compare the two approaches against each other.
