"""Data Dedup — editable file.

Available data: records.json with 300 records, each having:
  record_id, first_name, last_name, email, phone, company, city

golden_clusters: ground truth groupings (100 clusters)

Your job: implement find_duplicates(records) returning a list of clusters,
where each cluster is a list of record_ids that represent the same entity.

The harness calculates:
  - precision: fraction of predicted duplicate pairs that are true duplicates
  - recall: fraction of true duplicate pairs that were found
  - f1_score: harmonic mean of precision and recall

Metric: f1_score — HIGHER is better.
Baseline: return each record as its own cluster (no dedup = 0 recall, undefined precision -> f1=0).
"""


def find_duplicates(records: list[dict]) -> list[list[str]]:
    """Return list of clusters. Each cluster is a list of record_ids.

    Baseline: every record is its own cluster (no duplicates found).
    """
    return [[r["record_id"]] for r in records]
