# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-21

### Added

- `plasma-sensors install`: finds the motherboard's Super I/O sensor driver,
  loads it and persists it in `/etc/modules-load.d/plasma-sensors.conf`; adds
  a System Monitor widget to the Plasma panel with CPU and GPU temperature,
  and usage, power, chipset, board, NVMe, RAM and fans in its popup.
- `plasma-sensors detect`: shows what would be set up, without changing
  anything.
- `plasma-sensors uninstall`: removes the widget and the modules-load.d file.
- Options `--no-modules`, `--no-widget`, `--desktop`, `--no-restart`,
  `--dry-run` and `--lang en|es`.
- Messages and widget labels in English and Spanish.

[0.1.0]: https://github.com/sawady/plasma-sensors/releases/tag/v0.1.0
