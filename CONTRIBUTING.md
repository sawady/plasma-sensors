# Contributing

Thanks for helping! Issues and pull requests are welcome, in English or
Spanish.

## Sharing your hardware helps most

The sensor picking is heuristic. If the widget shows a wrong or missing
sensor on your machine, open an issue with:

- your motherboard, CPU and GPU,
- the output of `./plasma-sensors detect`,
- `sensors -j` and `kstatsviewer --list | grep -E '^(cpu/all|gpu|lmsensors|memory/physical)'`
  (the filter leaves out network names and the hostname).

Those two outputs can become a test fixture in `tests/fixtures/`, so the fix
stays fixed.

## Code

- One file, `plasma-sensors`, Python standard library only. Keep it that way so
  it runs on any distro without installing anything.
- The logic that decides what to show (`select_sensors`,
  `reorder_applet_order`, …) is pure and tested; the parts that touch the
  system are thin wrappers around it.
- Anything `install` writes must be recorded in the state file so that
  `uninstall` can undo it.
- Messages and widget labels live in `TEXT` at the top, in English and Spanish:
  add both.

## Checks

What CI runs:

```bash
pipx run ruff check .      # or: uvx ruff check .
python3 -m unittest discover -s tests -v
```

To try a change on your desktop, `./plasma-sensors install --dry-run` first,
then `install` and `uninstall`.
