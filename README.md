# AFM Force-Distance Curve Viewer

A browser-based tool for visualizing and exploring Atomic Force Microscopy (AFM) force-distance curve data from Park Systems PinPoint measurements.

**[Launch the app](https://afmviewer-gbvydokayqp2kwu7uk9wuq.streamlit.app/)**

## Features

- **Interactive topography map** — Click directly on the Z-height image to select pixels
- **Force-distance curve viewer** — Approach and retract curves displayed as interactive plots with hover tooltips for extracting data points
- **Line-by-line flattening** — Optional background subtraction that automatically masks tall features
- **Data export** — Download selected F-d curves, all extracted CSVs, or a full data package (curves + images + metadata)
- **Cross-platform** — Runs in any modern browser (Chrome, Safari, Firefox) on Windows, Mac, or Linux

## How to Use

1. **Upload your data** — Drag and drop a `.ps-ppt` file or a ZIP of pre-extracted CSV files
2. **Explore the topography** — Click on the Z-height map to select a pixel. Use the X/Y inputs for precise selection
3. **Inspect F-d curves** — Hover over the approach/retract plots to read force and separation values
4. **Toggle flattening** — Check "Flatten topography" to apply line-by-line background subtraction
5. **Download results** — Use the sidebar to export:
   - **Selected F-d curve** — CSV files for the current pixel with metadata embedded as header comments
   - **All CSVs** — Every extracted force-distance curve in a ZIP
   - **Full export** — All CSVs + selected curves + topography and F-d curve images + metadata

## Data Formats

### `.ps-ppt` Files (Park Systems PinPoint)

The `.ps-ppt` format is a proprietary binary file produced by [Park Systems](https://www.parksystems.com/) AFM instruments during PinPoint nanomechanical measurements. Each file contains a complete force-distance mapping dataset: the AFM tip approaches and retracts from the surface at every pixel in a grid (e.g., 64x64), recording force vs. separation at each location.

The app reads `.ps-ppt` files directly using Park Systems' `pspylib` library, which extracts the data into individual CSV files (one per pixel) for processing. This extraction happens automatically when you upload a `.ps-ppt` file.

### Extracted CSV Format

Each pixel produces one CSV file named `ppt-fd-slow{Y}-fast{X}.csv`, where X and Y are the pixel indices. The CSV contains:

**Metadata header (rows 1-10):**

| Row | Key | Example |
|---|---|---|
| 1 | `export.time` | `Mon Nov 17 13:38:29 2025` |
| 2 | `scan.geometry` | Scan dimensions, pixel count, rotation (JSON dict) |
| 3 | `cantilever.name` | Cantilever model (e.g., `FMR`) |
| 4 | `cantilever.cal` | Force constant (N/m), force slope, reference intensity |
| 5 | `cantilever.geometry` | Tip length, height, radius, width (nm) |
| 6 | `pinpoint.basic` | Approach/retract speeds (um/s) |
| 7 | `pinpoint.details` | Baseline, thresholds, z-control parameters |
| 8 | `sample` | Sample properties (e.g., Poisson ratio) |
| 9 | `file` | Original file paths |
| 10 | `info` | Channel definitions, timing, pixel index |

**Data columns (after header):**

| Column | Unit | Description |
|---|---|---|
| `Lfm` | volt | Lateral force microscopy signal |
| `Force` | nanonewton | Vertical force on the cantilever tip |
| `Separation` | micrometer | Tip-sample separation distance |

The data rows contain the full approach-retract cycle. The app splits the data at the maximum force point: everything before the peak is the **approach** curve, and everything after is the **retract** curve.

### Preparing a ZIP Upload

If you have already extracted the CSVs from a `.ps-ppt` file (e.g., using Park Systems' SmartScan software), you can upload them as a ZIP:

1. Locate the folder containing the extracted `ppt-fd-slow*-fast*.csv` files
2. Select all CSV files and compress them into a ZIP archive
3. Upload the ZIP to the app

The folder should contain files like:
```
ppt-fd-slow0-fast0.csv
ppt-fd-slow0-fast1.csv
ppt-fd-slow0-fast2.csv
...
ppt-fd-slow63-fast63.csv
```

## Running Locally

```bash
# Clone the repository
git clone https://github.com/scottdietrich/AFMviewer.git
cd AFMviewer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Dependencies

- [Streamlit](https://streamlit.io/) — Web app framework
- [Plotly](https://plotly.com/python/) — Interactive F-d curve plots
- [Matplotlib](https://matplotlib.org/) — Topography rendering
- [NumPy](https://numpy.org/) / [Pandas](https://pandas.pydata.org/) — Data processing
- [pspylib](https://www.parksystems.com/) — Park Systems data file reader (bundled)

## License

[MIT License](LICENSE)

## Author

Scott Dietrich — [Villanova University](https://www.villanova.edu/)
