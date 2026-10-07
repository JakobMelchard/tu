"""Executes tour.ipynb top to bottom (note 06): the notebook is the demo, this
is its test.  Same as the note's ``jupyter nbconvert --execute`` command, but
inside pytest; the kernel talks to this process over loopback only."""
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
nbclient = pytest.importorskip("nbclient")

NB = Path(__file__).with_name("tour.ipynb")


def test_tour_is_valid_and_runs_clean(tmp_path):
    nb = nbformat.read(NB, as_version=4)
    nbformat.validate(nb)
    nbclient.NotebookClient(nb, timeout=120, kernel_name="python3",
                            resources={"metadata": {"path": str(tmp_path)}}).execute()
    code = [c for c in nb.cells if c.cell_type == "code"]
    errors = [o for c in code for o in c.outputs if o.output_type == "error"]
    assert not errors, errors
    # executed once each, top to bottom: the hygiene note 06 §4 asks for
    assert [c.execution_count for c in code] == list(range(1, len(code) + 1))
