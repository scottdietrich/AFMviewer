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

## Supported File Formats

| Format | Description |
|---|---|
| `.ps-ppt` | Park Systems PinPoint raw data file (processed directly in the browser) |
| `.zip` | ZIP archive containing pre-extracted CSV files (`ppt-fd-slow*-fast*.csv`) |

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
