# plasma-sensors

[Español](README.es.md)

Show your PC's temperatures in the KDE Plasma 6 panel, with one command.

![CPU and GPU temperature in the Plasma panel](docs/panel.png)

KDE Plasma already ships a System Monitor widget that can show any sensor, but
getting there takes a few steps that aren't obvious:

- **Your motherboard's sensors are often missing.** The chip that reads the
  fans and board temperatures (a Super I/O chip such as Nuvoton NCT67xx or ITE
  IT87xx) needs a kernel driver that most distros, Bazzite included, don't load
  on their own. Without it you get no fan speeds and no chipset temperature.
- **Picking sensors by hand is tedious.** There are hundreds, many of them
  unplugged inputs that read 0 °C or 127 °C.

`plasma-sensors` does both for you:

1. Finds the right driver for your motherboard's sensor chip, loads it and
   makes it load on every boot.
2. Adds a System Monitor widget to your panel with the CPU and GPU temperature,
   and the rest in the popup that opens when you click it: CPU and GPU usage,
   GPU power, chipset and board temperature, each NVMe drive, RAM, and the fans
   that are spinning.

Everything it does is recorded and `plasma-sensors uninstall` undoes it.

Made on [Bazzite](https://bazzite.gg/) (KDE edition), works on any distro with
KDE Plasma 6: Fedora KDE, Kubuntu, KDE neon, Arch, openSUSE…

## Install

You need KDE Plasma 6, Python 3.9+, `lm_sensors` (`lm-sensors` on Debian and
Ubuntu) and `ksystemstats` (which provides `kstatsviewer`). Bazzite and Fedora
KDE already have all of them.

```bash
git clone https://github.com/sawady/plasma-sensors.git
cd plasma-sensors
./plasma-sensors detect     # see what it found, changes nothing
./plasma-sensors install
```

Loading kernel modules needs `sudo`, so it may ask for your password. To place
the widget right before the system tray, Plasma restarts once: the screen
flickers for a moment.

Options:

| Option | What it does |
| --- | --- |
| `--no-modules` | Skip the driver step: only add the widget. |
| `--no-widget` | Skip the widget: only set up the driver. |
| `--desktop` | Put the widget on the desktop instead of the panel. On OLED screens a fixed widget can burn in; the panel is safer. |
| `--no-restart` | Don't restart Plasma. The widget is added at the end of the panel; drag it in Edit Mode. |
| `--dry-run` | Print what would change and change nothing. |
| `--lang en\|es` | Language for messages and widget labels. By default it follows your locale. |

Running `install` again replaces the widget it added before, so you can rerun
it after adding a disk or a GPU.

## Customize

Right-click the widget → *Configure Sensors…*. The sensors at the top of the
list are the ones shown in the panel; the rest show in the popup. You can also
change the look there (text, line chart, bars, a grid of small charts).

## Uninstall

```bash
./plasma-sensors uninstall
```

It removes the widget and `/etc/modules-load.d/plasma-sensors.conf`. The driver
stays loaded until you reboot. It doesn't touch drivers you had set up
yourself.

## What it changes

- `/etc/modules-load.d/plasma-sensors.conf` (with `sudo`): the drivers to load
  on boot. Only drivers that found a chip and weren't already set to load.
- Your Plasma panel: one System Monitor widget, in
  `~/.config/plasma-org.kde.plasma.desktop-appletsrc` like any other widget.
- `~/.local/state/plasma-sensors/state.json`: what it did, for `uninstall`.

## How it finds the driver

It tries the in-kernel Super I/O drivers one by one (`nct6775`, `it87`,
`nct6683`, `f71882fg`, `w83627ehf`) and stops at the first one that finds a
chip. These drivers check for their chip and refuse to load when it isn't
there. A driver that loads but adds no sensors is unloaded. Then it tries the
ASUS drivers that add extra sensors on supported boards (`asus_ec_sensors`,
`asus_wmi_sensors`).

## Troubleshooting

**No motherboard chip found.** Run `sudo sensors-detect` and read its
summary: it knows many more chips. Some boards (several Gigabyte models with
newer ITE chips) need the out-of-tree
[it87 driver](https://github.com/frankcrawford/it87).

**`nct6775` fails with an ACPI resource conflict** (in `sudo dmesg`). Some
boards reserve the chip for the firmware. The common workaround is the kernel
argument `acpi_enforce_resources=lax`; read about its risks before using it.
On Bazzite: `rpm-ostree kargs --append=acpi_enforce_resources=lax`.

**Strange readings in `sensors`** (voltages with `ALARM`, a temperature of
127 °C, `intrusion ALARM`). These come from inputs with nothing connected or
from limits set to 0, and are usually harmless. The widget skips them.

**The widget shows no GPU.** KSystemStats reads NVIDIA cards through
`nvidia-smi` and AMD and Intel cards through the kernel. Check that
`kstatsviewer --list | grep gpu` lists a temperature.

## License

[MIT](LICENSE)
