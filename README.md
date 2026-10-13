[![PyPI](https://img.shields.io/pypi/v/cffview.svg?logo=python&logoColor=white)](https://pypi.org/project/cffview/)
[![Python versions](https://img.shields.io/pypi/pyversions/cffview.svg?color=orange&logo=python&label=python&logoColor=white)](https://pypi.org/project/cffview)
[![CI](https://github.com/aiwaonly/cffview/actions/workflows/build_wheels.yml/badge.svg)](https://github.com/aiwaonly/cffview/actions/workflows/build_wheels.yml)

[中文](README.zh.md)

# cffview

> CFF is an abbreviation for Ansys **C**ommon **F**luids **F**ormat.

A command-line tool for viewing Ansys Fluent `.cas.h5` / `.msh.h5` / `.dat.h5` files **without opening Fluent**.

- Read solver settings, materials, boundary conditions, discretisation schemes, and more directly from the HDF5 file.
- Browse the parsed settings in an interactive terminal UI (`--tui`).
- Visualise mesh or data with [PyVista](https://pyvista.org).

## Installation

### PyPI

```bash
pip install cffview
```

### From source

```bash
git clone https://github.com/aiwaonly/cffview.git
cd cffview
pip install .
```

## Usage

> [!IMPORTANT]
> Only tested with Ansys Fluent 25R2!

```
cffview <file> [options]
```

### Options

| Option | Description |
|---|---|
| `--version` | Print the Fluent version of file |
| `--extract` | Dump raw Scheme settings to `general.scm` / `boundary.scm` / `cortex.scm` |
| `--plotmesh` | Visualise the mesh interactively with PyVista |
| `--plotdata` | Visualise the data interactively with PyVista (may not work, depending on `vtkFLUENTCFFReader`) |
| `-t`, `--tui` | Browse the parsed settings in a terminal UI instead of printing them |
| `--solver` | Solver type, time, dimension, precision, turbulence model, energy, radiation, gravity, ... |
| `--mat [TYPE ...]`, `--materials` | Material properties grouped by material type (`fluid` / `solid`); filters match a material type or a material name (e.g. `--mat fluid`, `--mat air`) |
| `--bd [TYPE ...]`, `--boundary` | Boundary condition settings; filters match a boundary type (`vi` for `velocity-inlet`, whole word for single-word types) or a zone name (e.g. `--bd vi wall po`, `--bd shadow`) |
| `--interfaces` | Mesh interfaces settings |
| `--ne`, `--named-expressions` | Named expressions |
| `--cff`, `--custom-field-functions` | Custom field functions |
| `--units [KEYWORD ...]` | Show changed units (filtered by one or more keywords; empty means default SI units) |
| `--solution` | Solution methods and controls |
| `--rd`, `--report-definitions` | Report definitions |
| `--residuals` | Residual settings |
| `--monitorsets` | Monitor sets |
| `--plotsets` | Plot sets |
| `--convergencesets` | Convergence sets |
| `--cell`, `--cell-registers` | Cell registers settings |
| `--iter` | Iteration / time-step settings |
| `--surfaces` | Surfaces settings |
| `--mesh` | Graphics mesh settings |
| `--contours` | Graphics contours settings |
| `--vectors` | Graphics vectors settings |
| `--pathlines` | Graphics pathlines settings |
| `--xy-plot` | Graphics xy-plot settings |
| `--scene` | Graphics scene settings |
| `--parameters` | Input / output parameters |
| `--save` | Save the output to `file_name.json` (if `file_name` not specified, it is the same as input file) |
| `--plot [out\|xy\|dat]` | Plot a data file; without `TYPE`, infer from the file extension |

Multiple flags can be combined freely. Case settings flags (`--solver`, `--mat`, etc.) apply to `.cas.h5` files only.

> [!TIP]
> Long options can be abbreviated to any unambiguous prefix. For example,
> `--inter` works for `--interfaces` and `--vec` for `--vectors`. An ambiguous
> prefix (e.g. `--so`, which could match `--solver` or `--solution`) is
> rejected with an error.

### Examples

```bash
# Show all settings and save to JSON
cffview case.cas.h5 --save

# Show solver configuration and boundary conditions
cffview case.cas.h5 --solver --bd

# Visualise the mesh
cffview case.cas.h5 --plotmesh
cffview mesh.msh.h5

# Visualise the data
cffview case.cas.h5 --plotdata

# Check the Fluent version of file
cffview case.cas.h5 --version

# Extract raw Scheme strings for manual inspection
cffview case.cas.h5 --extract
```

### TUI

```bash
cffview case.cas.h5 --tui
```

The parsed settings are shown in a terminal UI instead of being printed: the case structure as a tree on the left, the selected entry as 4-space JSON on the right. Keys are coloured by nesting level, and the detail panel's border title shows the path and key count of the current entry.

| Key | Action |
|---|---|
| `↑` / `↓` | Move in the tree |
| `enter` | Select the entry: expands / collapses it when it has children, shows it on the right when it is a leaf |
| `space` | Expand or collapse the selected entry |
| `shift+←` / `shift+→` | Go to the parent / first child |
| `shift+↑` / `shift+↓` | Previous / next sibling |
| `shift+space` | Expand or collapse all entries |
| `pageup` / `pagedown`, `home` / `end` | Scroll the focused pane |
| `d` | Toggle the dark / light theme |
| `q` | Quit |

Clicking an entry selects it, and toggles it as well when it has children; either pane can also be scrolled with the mouse wheel.

### Demo

https://github.com/user-attachments/assets/7f97b559-87fa-4822-be9f-4e82b8c5cab6

## License

[BSD-3-Clause](LICENSE)
