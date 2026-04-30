"""Contract checks for shipped Home Assistant blueprints pack."""

from pathlib import Path


BLUEPRINT_DIR = Path(__file__).parents[1] / "blueprints" / "automation" / "zse_hdo_live"


def _read(name: str) -> str:
    return (BLUEPRINT_DIR / name).read_text(encoding="utf-8")


def test_blueprint_files_exist():
    assert (BLUEPRINT_DIR / "notify_low_tariff_on.yaml").exists()
    assert (BLUEPRINT_DIR / "boiler_by_tariff.yaml").exists()
    assert (BLUEPRINT_DIR / "reminder_before_switch.yaml").exists()


def test_blueprint_metadata_and_domain():
    for filename in [
        "notify_low_tariff_on.yaml",
        "boiler_by_tariff.yaml",
        "reminder_before_switch.yaml",
    ]:
        content = _read(filename)
        assert "blueprint:" in content
        assert "domain: automation" in content
        assert "input:" in content


def test_blueprints_reference_hdo_entities():
    notify = _read("notify_low_tariff_on.yaml")
    boiler = _read("boiler_by_tariff.yaml")
    reminder = _read("reminder_before_switch.yaml")

    assert "binary_sensor" in notify
    assert "binary_sensor" in boiler
    assert "sensor" in reminder
