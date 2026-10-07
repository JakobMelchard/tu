# data/

- `raw/`: as downloaded or collected; never modified by hand; git-ignored if large. Record the source URL, download date, licence and checksum here.
- `processed/`: produced from `raw/` by `make_dataset.py` (write it); regenerable, git-ignored.
- `splits.json`: the train/val/test index lists, produced once with the seed from `config.yaml` and committed.

Data card (fill in):

| Field | Value |
|---|---|
| Source | |
| Licence | |
| Samples (train / val / test) | |
| Input shape and dtype | |
| Label distribution | |
| Known issues (duplicates, noise, leakage risks) | |
| Preprocessing steps | |

The placeholder `load_dataset` in `train.py` generates synthetic shape images so the skeleton runs without any files here; replace it with a loader for `processed/`.
