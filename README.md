# F1 Data Analysis Toolkit

A collection of Python scripts for analysing Formula 1 timing and telemetry data, built on top of the [FastF1](https://github.com/theOehrly/Fast-F1) library. The scripts go beyond final race results to answer questions like:

- **Who had the most consistent race pace?** (lap-time distributions as violin plots)
- **How did the gap between drivers evolve lap by lap?** (cumulative time delta)
- **Where on the track is one driver faster than another?** (speed traces and time delta over distance)
- **How do drivers approach a corner differently?** (braking, turning and full-throttle phases)
- **How much does DRS actually help?** (top-speed gain and acceleration vs. speed with DRS on/off)

Every script produces a publication-style chart (dark theme, team colours) ready to share.

---

## Example outputs

> _Add your PNGs to an `images/` folder and they will show up here._

| Race pace distribution | Cumulative delta |
|---|---|
| ![Violin plot](images/violin_plot.png) | ![Cumulative delta](images/cumulative_delta.png) |

| Corner analysis | DRS effectiveness |
|---|---|
| ![Cornering](images/cornering.png) | ![DRS](images/drs_effectiveness.png) |

---

## Getting started

### Requirements

- Python 3.8+
- [FastF1](https://docs.fastf1.dev/), pandas, NumPy, Matplotlib, seaborn, SciPy, timple, openpyxl

```bash
git clone https://github.com/srao03/F1.git
cd F1
pip install -r requirements.txt
mkdir cache          # FastF1 stores downloaded session data here
```

> **Note:** the scripts were written in 2023 and use some older FastF1/pandas APIs (`session.load_laps()`, `DataFrame.append`). If you hit errors on recent versions, see [Known limitations](#known-limitations).

### Running a script

Each script is self-contained. Open it, edit the **inputs block** near the top (season, Grand Prix, session, drivers), then run:

```bash
python laptime_violinplots.py
```

The first run for a session downloads the data from the F1 live-timing API, which can take a minute. After that it is loaded from `cache/`.

Drivers are identified by their three-letter codes (`VER`, `HAM`, `LEC`, `NOR`, …). Sessions can be `'FP1'`, `'FP2'`, `'FP3'`, `'Qualifying'`, `'Sprint'` or `'RACE'`/`'R'`.

---

## Scripts

### Race pace & strategy

| Script | What it does | Key inputs | Output |
|---|---|---|---|
| `laptime_violinplots.py` | Violin plot of each driver's race lap times, overlaid with individual laps coloured by tyre compound and labelled with the tyre strategy. Pit-in and pit-out laps are removed, so the distributions reflect clean racing laps. Wide violins mean inconsistent pace; narrow ones mean consistent pace. | `session`, `drivers_to_visualize`, `RS` (strategy labels) | `ViolinPlots.png` |
| `laptime_trend.py` | Lap time vs. lap number for selected drivers. Each lap marker is coloured by tyre compound (soft/medium/hard), showing tyre degradation and how pace evolves within a stint. | `session`, `drvs`, `delete_laps`, lap-time window | On-screen plot |
| `Cummulative_Delta.py` | Gap of every driver to a reference driver (e.g. the race winner) at the end of each lap, using lap start times plus lap times. Shows where gaps opened or closed across the race. | `session`, `drivers`, `Reference_driver` | On-screen plot |
| `Cummulative_Delta2.py` | Same analysis for a larger field (15 drivers) with a tighter x-axis. | as above | On-screen plot |

### Single-lap telemetry

| Script | What it does | Key inputs | Output |
|---|---|---|---|
| `telemetry.py` | Speed trace vs. distance for two or more drivers on their fastest lap (or a chosen lap), with a lower panel showing the time delta to the fastest driver along the lap. Vertical markers highlight chosen corners. | `drivers`, `Fastestlap_Flag`, `lapno`, `turn_nos` | On-screen plot |
| `cornering_2_DRVS.py` | Corner-by-corner comparison of two drivers in a chosen section of track. Shows the speed trace, the running time gap, and a bar showing where each driver is **braking**, **turning** (coasting/partial throttle) or at **full throttle**. | `drivers`, `distance_min`/`distance_max`, `turn_nos` | On-screen plot |
| `cornering_3_DRVS.py` | Same corner analysis for three drivers. | as above | On-screen plot |

### DRS analysis

| Script | What it does | Key inputs | Output |
|---|---|---|---|
| `DRS_ON_OFF_Max_Speed.py` | Bar chart of each driver's maximum speed with DRS open vs. closed across a session, annotated with the speed gain (Δ km/h). | `session`, `drivers` | On-screen plot |
| `DRS_efficiency2.py` | Estimates DRS effectiveness by calculating acceleration from speed telemetry inside the DRS zones, then fitting acceleration-vs-speed curves (linear or quadratic) with DRS on and off. The gap between the two curves is the extra acceleration DRS gives. Per-driver plots plus a combined comparison. DRS-zone distances are pre-configured for Bahrain, Saudi Arabia, Australia, Azerbaijan and Miami (2023). | `Event_name`, `drivers`, `curve_fit_flg` | `<GP>_<DRIVER>.png`, `<GP>_All.png` |

### Track & utility scripts

| Script | What it does | Output |
|---|---|---|
| `get_GPS_coordinates.py` | Extracts X/Y position, time and speed for two drivers' fastest laps, plots their racing lines (optionally rotated), and exports the data to Excel. | Plots, `<DRIVER>_<GP>_<SESSION>_data.xlsx` |
| `get_distance_at_turns.py` | Plots the track map labelled with distance-from-start markers and turn numbers. Use it to find the distances to enter as `turn_nos` / `distance_min` / `distance_max` in the telemetry and cornering scripts. | Plots |
| `getSessionNames.py` | Prints the session names (FP1, Qualifying, Race, etc.) for a given event. Useful for weekends with a sprint format. | Console output |

---

## Methodology notes

- **Data source:** all data comes from the official F1 live-timing feed via FastF1, including lap timing, tyre compounds, car telemetry (speed, throttle, brake, DRS, ~4–5 Hz) and position data.
- **Clean-lap filtering:** pit-in and pit-out laps are excluded from pace analysis. Lap-time windows and lap-number exclusions (e.g. safety-car periods) can be set per script.
- **Cumulative gap:** `gap = (lap start time − reference lap start time) + (lap time − reference lap time)`, i.e. the time gap to the reference driver as they cross the line at the end of each lap.
- **Driver action classification** (cornering scripts): `Brake > 0` → Braking, `Throttle > 96%` → Full throttle, otherwise → Turning.
- **DRS state:** FastF1 exposes DRS as an integer code. Values `10/12/14` are treated as DRS open and `0/8` as closed.
- **Acceleration:** computed as Δspeed/Δtime between consecutive telemetry samples. Only accelerating samples inside DRS zones and above a minimum speed are used for the curve fits.

---

## Known limitations

- The scripts are configured by editing variables at the top of each file. There is no command-line interface yet.
- Team colours and driver pairings are hard-coded for the **2023** grid. Update `col_dict` for other seasons.
- Some scripts use APIs that newer library versions have deprecated or removed:
  - `session.load_laps(...)` → use `session.load(); laps = session.laps`
  - `DataFrame.append(...)` (removed in pandas 2.0) → use `pd.concat([...])`
  - `sns.violinplot(scale=...)` → `density_norm=...` in seaborn ≥ 0.13
- Some plots end without `plt.show()`/`savefig()` and are meant to be run in an interactive environment such as Spyder or Jupyter.

## Roadmap

- [ ] Move shared code (team colours, session loading, styling) into a common module
- [ ] Add a command-line interface (`--year 2023 --gp Miami --drivers VER PER`)
- [ ] Update to current FastF1 / pandas APIs
- [ ] Save every chart to an `outputs/` folder automatically

---

## Acknowledgements

- [FastF1](https://github.com/theOehrly/Fast-F1) by theOehrly, which made accessing F1 timing data possible.
- Data © Formula One World Championship Limited. This project is unofficial and not associated with Formula 1 companies.

## Author

**Shyamal Rao** ([@srao03](https://github.com/srao03))
