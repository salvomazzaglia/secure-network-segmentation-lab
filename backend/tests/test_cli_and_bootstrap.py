from __future__ import annotations

from secure_network_segmentation_lab.cli import main
from secure_network_segmentation_lab.database import open_database
from secure_network_segmentation_lab.lab_bootstrap import bootstrap_lab


def test_cli_version(capsys):
    assert main(["version"]) == 0
    assert "1.0.0" in capsys.readouterr().out


def test_cli_validate(capsys):
    assert main(["validate"]) == 0


def test_cli_adapter_plan(capsys):
    assert main(["adapter-plan", "--adapter", "radius"]) == 0
    out = capsys.readouterr().out.lower()
    assert "dry" in out or "connects" in out or "false" in out


def test_cli_inventory(capsys):
    assert main(["inventory"]) == 0


def test_cli_classify(capsys):
    assert main(["classify"]) == 0


def test_cli_evaluate_policy(capsys):
    assert main(["evaluate-policy"]) == 0


def test_cli_reachability(capsys):
    assert (
        main(
            ["reachability", "--source", "guest", "--destination", "management", "--service", "ssh"]
        )
        == 0
    )


def test_cli_drift(capsys):
    assert main(["drift"]) == 0


def test_cli_simulate(capsys):
    assert main(["simulate", "--scenario", "mixed", "--seed", "42", "--duration", "3"]) == 0


def test_bootstrap(tmp_path):
    db = open_database(tmp_path / "lab.sqlite3")
    db = bootstrap_lab(db)
    assert len(db.list_devices()) >= 35
