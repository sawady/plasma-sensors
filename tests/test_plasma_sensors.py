import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"

_loader = importlib.machinery.SourceFileLoader("plasma_sensors", str(ROOT / "plasma-sensors"))
_spec = importlib.util.spec_from_loader("plasma_sensors", _loader)
ps = importlib.util.module_from_spec(_spec)
_loader.exec_module(ps)


def load(name):
    ids = ps.parse_kstats_list((FIXTURES / f"{name}.kstats.txt").read_text())
    sensors = json.loads((FIXTURES / f"{name}.sensors.json").read_text())
    return ids, sensors


class SelectSensorsIntelNvidia(unittest.TestCase):
    """ASUS TUF Z690 (Nuvoton NCT6798D), i7-12700K, RTX 3080 Ti, two NVMe."""

    def setUp(self):
        self.panel, self.popup = ps.select_sensors(*load("z690-nvidia"), lang="en")
        self.popup_ids = dict(self.popup)

    def test_panel_has_cpu_and_gpu_temperature(self):
        self.assertEqual(
            self.panel,
            [("cpu/all/maximumTemperature", "CPU"), ("gpu/gpu0/temperature", "GPU")],
        )

    def test_popup_has_usage_power_and_ram(self):
        for sid in ("cpu/all/usage", "gpu/gpu0/usage", "gpu/gpu0/power", "memory/physical/usedPercent"):
            self.assertIn(sid, self.popup_ids)

    def test_chipset_and_board(self):
        self.assertEqual(self.popup_ids["lmsensors/nct6798-isa-0290/temp11"], "Chipset")
        self.assertEqual(self.popup_ids["lmsensors/nct6798-isa-0290/temp1"], "Board")

    def test_bogus_chipset_readings_are_skipped(self):
        # PCH_CHIP_CPU_MAX_TEMP and PCH_CPU_TEMP read 0, AUXTIN4 reads 127.
        for feat in ("temp10", "temp12", "temp7"):
            self.assertNotIn(f"lmsensors/nct6798-isa-0290/{feat}", self.popup_ids)

    def test_both_nvme_drives_are_numbered(self):
        self.assertEqual(self.popup_ids["lmsensors/nvme-pci-0200/temp1"], "NVMe 1")
        self.assertEqual(self.popup_ids["lmsensors/nvme-pci-0400/temp1"], "NVMe 2")

    def test_only_spinning_fans(self):
        fans = [sid for sid in self.popup_ids if "/fan" in sid]
        self.assertEqual(
            fans,
            [f"lmsensors/nct6798-isa-0290/fan{n}" for n in (1, 2, 3, 4, 7)],
        )
        self.assertEqual(self.popup_ids["lmsensors/nct6798-isa-0290/fan7"], "Fan 7")

    def test_no_duplicates(self):
        ids = [s for s, _ in self.panel + self.popup]
        self.assertEqual(len(ids), len(set(ids)))

    def test_spanish_labels(self):
        _, popup = ps.select_sensors(*load("z690-nvidia"), lang="es")
        labels = dict(popup)
        self.assertEqual(labels["cpu/all/usage"], "CPU uso")
        self.assertEqual(labels["lmsensors/nct6798-isa-0290/fan1"], "Ventilador 1")
        self.assertEqual(labels["lmsensors/nct6798-isa-0290/temp1"], "Placa")


class SelectSensorsAmd(unittest.TestCase):
    """Ryzen (k10temp), Radeon (amdgpu), ITE IT8688E, one NVMe."""

    def setUp(self):
        self.panel, self.popup = ps.select_sensors(*load("amd-it87"), lang="en")
        self.popup_ids = dict(self.popup)

    def test_panel(self):
        self.assertEqual([label for _, label in self.panel], ["CPU", "GPU"])

    def test_single_nvme_is_not_numbered(self):
        self.assertEqual(self.popup_ids["lmsensors/nvme-pci-0100/temp1"], "NVMe")

    def test_unlabeled_it87_temps_are_not_guessed(self):
        self.assertFalse(any("/temp" in sid for sid in self.popup_ids if "it8688" in sid))

    def test_stopped_fan_is_skipped(self):
        self.assertIn("lmsensors/it8688-isa-0a40/fan1", self.popup_ids)
        self.assertNotIn("lmsensors/it8688-isa-0a40/fan2", self.popup_ids)


class SelectSensorsEdgeCases(unittest.TestCase):
    def test_multiple_gpus_are_numbered(self):
        ids = {f"gpu/gpu{n}/temperature": "" for n in (0, 1)}
        panel, _ = ps.select_sensors(ids, {}, lang="en")
        self.assertEqual([label for _, label in panel], ["GPU 1", "GPU 2"])

    def test_promotes_a_temperature_when_no_cpu_or_gpu(self):
        ids = {"lmsensors/nvme-pci-0100/temp1": "Composite"}
        sensors = {"nvme-pci-0100": {"Composite": {"temp1_input": 40.0}}}
        panel, popup = ps.select_sensors(ids, sensors, lang="en")
        self.assertEqual(panel, [("lmsensors/nvme-pci-0100/temp1", "NVMe")])
        self.assertEqual(popup, [])

    def test_sensors_not_in_ksystemstats_are_ignored(self):
        sensors = {"nvme-pci-0100": {"Composite": {"temp1_input": 40.0}}}
        self.assertEqual(ps.select_sensors({}, sensors, lang="en"), ([], []))


class ReorderAppletOrder(unittest.TestCase):
    TEXT = (
        "[Containments][2][Applets][7]\nplugin=org.kde.plasma.systemtray\n\n"
        "[Containments][2][General]\nAppletOrder=3;4;33;6;7;21;22;36\n\n"
        "[Containments][9][General]\nAppletOrder=1;2\n"
    )

    def test_moves_widget_before_target(self):
        out = ps.reorder_applet_order(self.TEXT, 2, 36, 7)
        self.assertIn("AppletOrder=3;4;33;6;36;7;21;22\n", out)
        self.assertIn("AppletOrder=1;2\n", out)

    def test_widget_missing_from_order_is_inserted(self):
        out = ps.reorder_applet_order(self.TEXT, 2, 99, 7)
        self.assertIn("AppletOrder=3;4;33;6;99;7;21;22;36\n", out)

    def test_unknown_target_or_containment(self):
        self.assertIsNone(ps.reorder_applet_order(self.TEXT, 2, 36, 1234))
        self.assertIsNone(ps.reorder_applet_order(self.TEXT, 5, 36, 7))


class Misc(unittest.TestCase):
    def test_detect_lang(self):
        self.assertEqual(ps.detect_lang({"LANG": "es_AR.UTF-8"}), "es")
        self.assertEqual(ps.detect_lang({"LANG": "en_US.UTF-8"}), "en")
        self.assertEqual(ps.detect_lang({"LC_ALL": "C", "LANG": "es_AR.UTF-8"}), "en")
        self.assertEqual(ps.detect_lang({}), "en")

    def test_persisted_modules(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.conf").write_text("# comment\nnct6775\n\nasus-ec-sensors # inline\n")
            (Path(d) / "b.txt").write_text("it87\n")
            self.assertEqual(
                ps.persisted_modules([Path(d), Path(d) / "missing"]),
                {"nct6775", "asus_ec_sensors"},
            )

    def test_hwmon_features_uses_raw_feature_names(self):
        feats = ps.hwmon_features(json.loads((FIXTURES / "z690-nvidia.sensors.json").read_text()))
        triples = {(c, f, label) for c, f, label, _ in feats}
        self.assertIn(("nct6798-isa-0290", "temp11", "PCH_CHIP_TEMP"), triples)
        self.assertIn(("nvme-pci-0200", "temp1", "Composite"), triples)
        self.assertIn(("nct6798-isa-0290", "fan7", "fan7"), triples)

    def test_widget_script_embeds_valid_json(self):
        cfg = {"title": 'Sen"sores', "labels": {"a/b": "x'y"}, "previous": None}
        script = ps.widget_script(cfg)
        first = script.strip().splitlines()[0]
        self.assertTrue(first.startswith("var cfg = ") and first.endswith(";"))
        self.assertEqual(json.loads(first[len("var cfg = "):-1]), cfg)


if __name__ == "__main__":
    unittest.main()
