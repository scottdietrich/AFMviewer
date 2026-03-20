# -*- coding: utf-8 -*-
"""
AFM Viewer — Streamlit Web App

Interactive browser-based viewer for AFM force-distance curve data.
Upload a ZIP of extracted CSVs (or a .ps-ppt file if pspylib is installed),
view topography, click to inspect F-d curves, and download results.

Author: Scott Dietrich
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import io
import zipfile
import tempfile
import shutil
import glob as globmod

from DataUtils import getHeightandDeformation, find_first_crossing

# Optional: .ps-ppt support requires pspylib
try:
    from Extractor import extract
    PSPYLIB_AVAILABLE = True
except ImportError:
    PSPYLIB_AVAILABLE = False

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AFM Viewer",
    page_icon=":microscope:",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS = dict(
    csv_dir=None,
    Z_raw=None,
    Z_flat=None,
    Z=None,
    X=None,
    Y=None,
    scan_info=None,
    metadata_raw=None,
    dataset_name="",
    selected_nx=None,
    selected_ny=None,
    approach=None,
    retract=None,
    flatten=False,
    temp_dir=None,
    loaded=False,
    _all_csv_zip=None,       # cached zip bytes
)
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Data helpers  (adapted from AFMViewer.py — logic unchanged)
# ---------------------------------------------------------------------------
def get_file_data(csv_dir):
    """Extract scan parameters and metadata from the first CSV."""
    fpath = os.path.join(csv_dir, "ppt-fd-slow0-fast0.csv")
    if not os.path.isfile(fpath):
        raise FileNotFoundError(f"Cannot find {fpath}")

    meta = pd.read_csv(fpath, nrows=8)

    # Cantilever stiffness
    cantilever_cal = str(meta.iloc[2, 1])
    idx_fc = cantilever_cal.find("forceConstant")
    idx_fs = cantilever_cal.find("forceSlope")
    kTIP = float(cantilever_cal[idx_fc + len("forceConstant") + 3 : idx_fs - 3])

    # Scan geometry
    sg = str(meta.iloc[0, 1])
    idx_h  = sg.find("height")
    idx_ox = sg.find("offsetX")
    idx_w  = sg.find("width")
    idx_end = sg.find("}")
    scanHeight = 1000 * float(sg[idx_h + len("height") + 3 : idx_ox - 3])
    scanWidth  = 1000 * float(sg[idx_w + len("width") + 3 : idx_end])

    idx_ph  = sg.find("pixelHeight")
    idx_pw  = sg.find("pixelWidth")
    idx_rot = sg.find("rotation")
    idx_rot_end = idx_rot + sg[idx_rot : idx_rot + len("rotation") + 7].find(",")
    Xpixels = int(sg[idx_ph + len("pixelHeight") + 3 : idx_pw - 3])
    Ypixels = int(sg[idx_pw + len("pixelWidth") + 3 : idx_rot - 3])
    rot     = int(sg[idx_rot + len("rotation") + 2 : idx_rot_end])

    metadata_raw = {}
    keys = ["scan.geometry", "cantilever.name", "cantilever.cal",
            "cantilever.geometry", "pinpoint.basic", "pinpoint.details",
            "sample", "file"]
    for i, key in enumerate(keys):
        metadata_raw[key] = str(meta.iloc[i, 1])

    return [scanHeight, scanWidth, Xpixels, Ypixels, rot, kTIP], metadata_raw


def get_fd_curve(csv_dir, nx, ny):
    """Load a single F-d curve, splitting into approach and retract."""
    csv_file = os.path.join(csv_dir, f"ppt-fd-slow{ny}-fast{nx}.csv")
    if not os.path.isfile(csv_file):
        return pd.DataFrame(), pd.DataFrame()
    try:
        data = pd.read_csv(
            csv_file,
            skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12],
            usecols=['Lfm', 'Force', 'Separation'])
        data.columns = ['Lfm (V)', 'F (nN)', 'Separation (um)']
    except (ValueError, KeyError):
        return pd.DataFrame(), pd.DataFrame()

    if data.empty:
        return pd.DataFrame(), pd.DataFrame()

    imax = data['F (nN)'].idxmax()
    return data.iloc[:imax].copy(), data.iloc[imax:].copy()


def flatten_z(Z_raw, scanH, Xpix, Ypix):
    """Masked line-by-line flattening that excludes tall features."""
    Z = Z_raw.copy()
    coords = np.linspace(0, scanH, Xpix)
    for j in range(Ypix):
        line = Z[:, j]
        valid = ~np.isnan(line)
        if np.sum(valid) < 3:
            continue
        bg_mask = valid.copy()
        for _ in range(2):
            if np.sum(bg_mask) < 3:
                break
            c = np.polyfit(coords[bg_mask], line[bg_mask], 1)
            residuals = line - np.polyval(c, coords)
            res_bg = residuals[bg_mask]
            threshold = np.median(res_bg) + 1.5 * np.std(res_bg)
            bg_mask = valid & (residuals <= threshold)
        if np.sum(bg_mask) >= 2:
            c = np.polyfit(coords[bg_mask], line[bg_mask], 1)
            Z[valid, j] = line[valid] - np.polyval(c, coords[valid])
            Z[valid, j] -= np.nanmin(Z[valid, j])
    return Z


def compute_topography(csv_dir, scan_info, progress_bar):
    """Compute Z-height topography from all F-d curves."""
    scanH, scanW, Xpix, Ypix, rot, kTIP = scan_info
    Z_raw = np.zeros([Xpix, Ypix])
    total = Xpix * Ypix
    count = 0
    for j in range(Ypix):
        for i in range(Xpix):
            approach, _ = get_fd_curve(csv_dir, i, j)
            if not approach.empty:
                try:
                    Zij, _, _, _, _ = getHeightandDeformation(approach)
                    Z_raw[i, j] = Zij
                except Exception:
                    Z_raw[i, j] = np.nan
            else:
                Z_raw[i, j] = np.nan
            count += 1
            if count % max(1, total // 100) == 0:
                progress_bar.progress(count / total,
                                      text=f"Computing topography... {count}/{total}")
    progress_bar.progress(1.0, text="Topography complete.")
    return Z_raw


# ---------------------------------------------------------------------------
# Metadata / download helpers
# ---------------------------------------------------------------------------
def build_metadata_text(dataset_name, scan_info, metadata_raw, selected_pixel=None):
    lines = [f"Dataset: {dataset_name}"]
    if selected_pixel:
        lines.append(f"Selected Pixel: ({selected_pixel[0]}, {selected_pixel[1]})")
    if scan_info:
        scanH, scanW, Xpix, Ypix, rot, kTIP = scan_info
        lines.append(f"Scan Size: {scanW:.1f} x {scanH:.1f} nm")
        lines.append(f"Pixels: {Xpix} x {Ypix}")
        lines.append(f"Rotation: {rot} deg")
        lines.append(f"Tip Stiffness: {kTIP:.4f} N/m")
    if metadata_raw:
        lines.append("\n--- Raw Metadata ---")
        for key, val in metadata_raw.items():
            lines.append(f"{key}: {val}")
    return "\n".join(lines)


def _csv_with_metadata_header(df, meta_txt):
    """Return CSV string with metadata embedded as # comment lines at the top."""
    header_lines = ["# " + line for line in meta_txt.splitlines()]
    return "\n".join(header_lines) + "\n" + df.to_csv(index=False)


def make_selected_zip(dataset_name, scan_info, metadata_raw, nx, ny, approach, retract):
    """ZIP with selected F-d curve CSVs (metadata embedded in each CSV)."""
    buf = io.BytesIO()
    prefix = f"{dataset_name}_px{nx}-{ny}"
    meta_txt = build_metadata_text(dataset_name, scan_info, metadata_raw,
                                   selected_pixel=(nx, ny))
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        if approach is not None and not approach.empty:
            df_a = pd.DataFrame({
                'Separation (nm)': approach['Separation (um)'].values * 1000,
                'Force (nN)': approach['F (nN)'].values,
            })
            zf.writestr(f"{prefix}_approach.csv",
                        _csv_with_metadata_header(df_a, meta_txt))
        if retract is not None and not retract.empty:
            df_r = pd.DataFrame({
                'Separation (nm)': retract['Separation (um)'].values * 1000,
                'Force (nN)': retract['F (nN)'].values,
            })
            zf.writestr(f"{prefix}_retract.csv",
                        _csv_with_metadata_header(df_r, meta_txt))
    buf.seek(0)
    return buf


def _build_all_csv_zip(csv_dir, dataset_name, scan_info, metadata_raw):
    """ZIP with every extracted CSV + metadata, all inside a named folder."""
    buf = io.BytesIO()
    meta_txt = build_metadata_text(dataset_name, scan_info, metadata_raw)
    folder = f"{dataset_name}_csv"
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(globmod.glob(os.path.join(csv_dir, "ppt-fd-*.csv"))):
            zf.write(fpath, arcname=f"{folder}/{os.path.basename(fpath)}")
        zf.writestr(f"{folder}/metadata.txt", meta_txt)
    buf.seek(0)
    return buf.getvalue()


def fig_to_png_bytes(fig):
    """Render a matplotlib figure to PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    buf.seek(0)
    return buf.read()


def make_full_zip(csv_dir, dataset_name, scan_info, metadata_raw,
                  nx, ny, approach, retract, Z, X, Y):
    """Full export: all CSVs + selected curves + images + metadata."""
    buf = io.BytesIO()
    prefix = f"{dataset_name}_px{nx}-{ny}"
    meta_txt = build_metadata_text(dataset_name, scan_info, metadata_raw,
                                   selected_pixel=(nx, ny))
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # All raw CSVs in a subfolder
        for fpath in sorted(globmod.glob(os.path.join(csv_dir, "ppt-fd-*.csv"))):
            zf.write(fpath, arcname=f"all_csv/{os.path.basename(fpath)}")

        # Selected F-d curves
        if approach is not None and not approach.empty:
            df_a = pd.DataFrame({
                'Separation (nm)': approach['Separation (um)'].values * 1000,
                'Force (nN)': approach['F (nN)'].values,
            })
            zf.writestr(f"{prefix}_approach.csv", df_a.to_csv(index=False))
        if retract is not None and not retract.empty:
            df_r = pd.DataFrame({
                'Separation (nm)': retract['Separation (um)'].values * 1000,
                'Force (nN)': retract['F (nN)'].values,
            })
            zf.writestr(f"{prefix}_retract.csv", df_r.to_csv(index=False))

        # Topography image
        topo_fig, ax_t = plt.subplots(figsize=(6, 5))
        pd_export = np.flip(np.transpose(Z))
        cf = ax_t.contourf(X, Y, pd_export, 100)
        topo_fig.colorbar(cf, ax=ax_t, shrink=0.9).ax.tick_params(labelsize=8)
        xm, ym = pixel_to_plot(nx, ny, scan_info)
        ax_t.plot(xm, ym, 'x', color='red', markersize=10, markeredgewidth=2)
        ax_t.set_title("Z-Height (nm)")
        ax_t.axis('scaled')
        ax_t.set_xlabel("nm")
        ax_t.set_ylabel("nm")
        topo_fig.tight_layout()
        zf.writestr(f"{prefix}_topography.png", fig_to_png_bytes(topo_fig))
        plt.close(topo_fig)

        # F-d curves image
        fd_fig, (ax_a, ax_r) = plt.subplots(2, 1, figsize=(6, 7))
        if approach is not None and not approach.empty:
            sep_a = approach['Separation (um)'].values * 1000
            f_a = approach['F (nN)'].values
            ax_a.plot(sep_a, f_a, color='tab:blue', linewidth=1)
            ax_a.axhline(linewidth=0.5, color='gray', zorder=0)
            ax_a.set_xlabel("Separation (nm)")
            ax_a.set_ylabel("Force (nN)")
            ax_a.set_title("Approach")
        if retract is not None and not retract.empty:
            sep_r = retract['Separation (um)'].values * 1000
            f_r = retract['F (nN)'].values
            ax_r.plot(sep_r, f_r, color='tab:orange', linewidth=1)
            ax_r.axhline(linewidth=0.5, color='gray', zorder=0)
        ax_r.set_xlabel("Separation (nm)")
        ax_r.set_ylabel("Force (nN)")
        ax_r.set_title("Retract")
        fd_fig.tight_layout()
        zf.writestr(f"{prefix}_fd_curves.png", fig_to_png_bytes(fd_fig))
        plt.close(fd_fig)

        zf.writestr("metadata.txt", meta_txt)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Coordinate mapping helpers
# ---------------------------------------------------------------------------
def pixel_to_plot(nx, ny, scan_info):
    """Convert pixel indices to plot coordinates."""
    scanH, scanW, Xpix, Ypix, rot, kTIP = scan_info
    x_mark = nx * (scanW / Xpix)
    y_mark = (Ypix - 1 - ny) * (scanH / Ypix)
    return x_mark, y_mark


def plot_to_pixel(xclick, yclick, scan_info):
    """Convert plot coordinates to pixel indices."""
    scanH, scanW, Xpix, Ypix, rot, kTIP = scan_info
    nx = int(round(xclick * Xpix / scanW))
    ny = Ypix - 1 - int(round(yclick * Ypix / scanH))
    nx = max(0, min(nx, Xpix - 1))
    ny = max(0, min(ny, Ypix - 1))
    return nx, ny


# ---------------------------------------------------------------------------
# Topography image builder
# ---------------------------------------------------------------------------
TOPO_DISPLAY_PX = 350   # rendered image size (square)

def build_topo_image(Z, Xpix, Ypix, selected_nx, selected_ny):
    """Render Z-height data as a clickable PIL image with marker overlay.

    In the original app, contourf(X, Y, flip(transpose(Z))) displays with
    Y increasing upward.  For a PIL image (row 0 = top), we use just
    transpose(Z) so that row 0 = ny=0 (top of scan) — matching the visual
    orientation of the contourf plot.
    """
    plot_data = np.transpose(Z)  # shape (Ypix, Xpix) — no flip for PIL
    vmin = np.nanmin(plot_data)
    vmax = np.nanmax(plot_data)
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.viridis

    Z_safe = np.where(np.isnan(plot_data), vmin, plot_data)
    rgba = cmap(norm(Z_safe))
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)

    img = Image.fromarray(rgb)
    img = img.resize((TOPO_DISPLAY_PX, TOPO_DISPLAY_PX), Image.NEAREST)

    # Draw red X marker for selected pixel
    if selected_nx is not None:
        draw = ImageDraw.Draw(img)
        mx = int((selected_nx + 0.5) * TOPO_DISPLAY_PX / Xpix)
        my = int((selected_ny + 0.5) * TOPO_DISPLAY_PX / Ypix)
        s = max(6, TOPO_DISPLAY_PX // 50)
        draw.line([(mx - s, my - s), (mx + s, my + s)], fill=(255, 50, 50), width=3)
        draw.line([(mx - s, my + s), (mx + s, my - s)], fill=(255, 50, 50), width=3)

    return img, vmin, vmax


# ---------------------------------------------------------------------------
# Load / process uploaded data
# ---------------------------------------------------------------------------
def process_upload(uploaded, upload_type):
    """Handle file upload: extract, compute topography, store in session."""
    # Clean up old temp dir
    if st.session_state.temp_dir and os.path.isdir(st.session_state.temp_dir):
        shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)

    temp_dir = tempfile.mkdtemp(prefix="afmviewer_")
    st.session_state.temp_dir = temp_dir

    if upload_type == "zip":
        with zipfile.ZipFile(io.BytesIO(uploaded.read()), 'r') as zf:
            zf.extractall(temp_dir)
        csv_dir = temp_dir
        if not os.path.isfile(os.path.join(csv_dir, "ppt-fd-slow0-fast0.csv")):
            for item in os.listdir(temp_dir):
                subdir = os.path.join(temp_dir, item)
                if os.path.isdir(subdir):
                    if os.path.isfile(os.path.join(subdir, "ppt-fd-slow0-fast0.csv")):
                        csv_dir = subdir
                        break
    else:
        ppt_path = os.path.join(temp_dir, uploaded.name)
        with open(ppt_path, 'wb') as f:
            f.write(uploaded.read())
        dataname = os.path.splitext(uploaded.name)[0]
        extract(temp_dir + "/", dataname)
        csv_dir = os.path.join(temp_dir, dataname)

    st.session_state.csv_dir = csv_dir
    st.session_state.dataset_name = os.path.splitext(uploaded.name)[0]

    # Load scan info
    scan_info, metadata_raw = get_file_data(csv_dir)
    st.session_state.scan_info = scan_info
    st.session_state.metadata_raw = metadata_raw

    # Compute topography
    progress = st.progress(0, text="Computing topography...")
    Z_raw = compute_topography(csv_dir, scan_info, progress)
    progress.empty()

    scanH, scanW, Xpix, Ypix, rot, kTIP = scan_info
    Z_flat = flatten_z(Z_raw, scanH, Xpix, Ypix)

    st.session_state.Z_raw = Z_raw
    st.session_state.Z_flat = Z_flat
    st.session_state.Z = Z_flat if st.session_state.flatten else Z_raw
    st.session_state.X = np.linspace(0, scanW, Xpix)
    st.session_state.Y = np.linspace(0, scanH, Ypix)

    # Pre-build the all-CSV zip once
    st.session_state._all_csv_zip = _build_all_csv_zip(
        csv_dir, st.session_state.dataset_name, scan_info, metadata_raw)

    # Auto-select highest point
    Z = st.session_state.Z
    if not np.all(np.isnan(Z)):
        plot_data = np.flip(np.transpose(Z))
        i_plot, j_plot = np.unravel_index(np.nanargmax(plot_data), plot_data.shape)
        nx_auto = j_plot
        ny_auto = Ypix - 1 - i_plot
        st.session_state.selected_nx = nx_auto
        st.session_state.selected_ny = ny_auto
        approach, retract = get_fd_curve(csv_dir, nx_auto, ny_auto)
        st.session_state.approach = approach
        st.session_state.retract = retract

    st.session_state.loaded = True


def select_pixel(nx, ny):
    """Update the selected pixel and load its F-d curve."""
    if nx == st.session_state.selected_nx and ny == st.session_state.selected_ny:
        return
    st.session_state.selected_nx = nx
    st.session_state.selected_ny = ny
    approach, retract = get_fd_curve(st.session_state.csv_dir, nx, ny)
    st.session_state.approach = approach
    st.session_state.retract = retract


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

# Compact CSS — moderate density, comfortable reading
st.markdown("""
<style>
    /* Global scale — 90% is a nice middle ground */
    .main .block-container { zoom: 0.9; padding-top: 1.5rem; padding-bottom: 0rem; max-width: 100%; }
    /* Headers */
    h1 { font-size: 1.4rem !important; margin: 0 0 0.2rem 0 !important; }
    h2 { font-size: 1.05rem !important; margin: 0.1rem 0 !important; }
    h3 { font-size: 0.95rem !important; margin: 0.1rem 0 !important; }
    /* Reduce gaps between elements */
    .element-container { margin-bottom: 0.1rem !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.2rem; }
    /* Compact widgets */
    .stCheckbox { margin-bottom: -0.5rem; }
    .stNumberInput { margin-bottom: -0.5rem; }
    .stCaption { font-size: 0.75rem !important; }
    .stMetric { padding: 0 !important; }
    .stMetric label { font-size: 0.75rem !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
    /* Sidebar */
    section[data-testid="stSidebar"] .stMarkdown p { font-size: 0.82rem; }
    section[data-testid="stSidebar"] h2 { font-size: 0.95rem !important; }
    /* Plotly charts */
    .stPlotlyChart { margin-bottom: -0.3rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("AFM Force-Distance Curve Viewer")

# ---- Sidebar: Upload + Downloads ----
with st.sidebar:
    st.header("Load Dataset")

    uploaded = st.file_uploader(
        "Upload a ZIP of extracted CSVs or a .ps-ppt file",
        type=None)  # allow all file types — .ps-ppt not recognized by browser filters

    if uploaded is not None:
        is_ppt = uploaded.name.lower().endswith(".ps-ppt")
        is_zip = uploaded.name.lower().endswith(".zip")
        if not is_ppt and not is_zip:
            st.error("Please upload a .ps-ppt or .zip file.")
        else:
            file_key = f"{uploaded.name}_{uploaded.size}"
            if st.session_state.get('_upload_key') != file_key:
                st.session_state['_upload_key'] = file_key
                upload_type = "ppt" if is_ppt else "zip"
                with st.spinner("Processing..."):
                    try:
                        process_upload(uploaded, upload_type)
                    except Exception as e:
                        st.error(f"Error loading dataset: {e}")
                        st.session_state.loaded = False

    # Downloads (only after data is loaded)
    if st.session_state.loaded:
        st.divider()
        st.header("Download Data")

        nx_sel = st.session_state.selected_nx
        ny_sel = st.session_state.selected_ny
        ds_name = st.session_state.dataset_name

        # 1. Selected F-d curve
        st.markdown("**Selected F-d curve**")
        if nx_sel is not None and st.session_state.approach is not None:
            zip_sel = make_selected_zip(
                ds_name, st.session_state.scan_info,
                st.session_state.metadata_raw,
                nx_sel, ny_sel,
                st.session_state.approach, st.session_state.retract)
            st.download_button(
                f"Pixel ({nx_sel}, {ny_sel}) CSVs + metadata",
                data=zip_sel,
                file_name=f"{ds_name}_px{nx_sel}-{ny_sel}.zip",
                mime="application/zip",
                use_container_width=True)
        else:
            st.caption("Select a pixel first.")

        # 2. All CSVs
        st.markdown("**All extracted CSVs**")
        if st.session_state._all_csv_zip is not None:
            st.download_button(
                "All CSVs + metadata",
                data=st.session_state._all_csv_zip,
                file_name=f"{ds_name}_all_csv.zip",
                mime="application/zip",
                use_container_width=True)

        # 3. Full export
        st.markdown("**Full export**")
        if nx_sel is not None and st.session_state.approach is not None:
            if st.button("Prepare full export", key="prep_full",
                         use_container_width=True):
                with st.spinner("Building export..."):
                    zip_full = make_full_zip(
                        st.session_state.csv_dir, ds_name,
                        st.session_state.scan_info, st.session_state.metadata_raw,
                        nx_sel, ny_sel,
                        st.session_state.approach, st.session_state.retract,
                        st.session_state.Z, st.session_state.X, st.session_state.Y)
                    st.session_state._full_zip = zip_full.getvalue()
                    st.session_state._full_zip_label = (
                        f"{ds_name}_px{nx_sel}-{ny_sel}_full.zip")
                    st.rerun()
            if st.session_state.get('_full_zip'):
                st.download_button(
                    "Download full export",
                    data=st.session_state._full_zip,
                    file_name=st.session_state._full_zip_label,
                    mime="application/zip",
                    use_container_width=True)
        else:
            st.caption("Select a pixel first.")


# ---- Main area ----
if st.session_state.loaded:
    scanH, scanW, Xpix, Ypix, rot, kTIP = st.session_state.scan_info

    # ---- Dataset info bar ----
    info_cols = st.columns([2, 1, 1, 1])
    with info_cols[0]:
        st.markdown(f"**{st.session_state.dataset_name}**")
    with info_cols[1]:
        st.caption(f"Scan: {scanW:.0f} x {scanH:.0f} nm")
    with info_cols[2]:
        st.caption(f"Pixels: {Xpix} x {Ypix}")
    with info_cols[3]:
        st.caption(f"Tip k: {kTIP:.3f} N/m")

    # ---- Two-column layout: Topography | F-d curves ----
    col_topo, col_fd = st.columns([2, 3])

    # ---- Topography (clickable image) ----
    with col_topo:
        st.subheader("Z-Height Topography")

        # Flatten toggle right above the image
        flatten = st.checkbox("Flatten topography (line-by-line)",
                              value=st.session_state.flatten)
        if flatten != st.session_state.flatten:
            st.session_state.flatten = flatten
            st.session_state.Z = (st.session_state.Z_flat if flatten
                                  else st.session_state.Z_raw)
            st.rerun()

        topo_img, z_min, z_max = build_topo_image(
            st.session_state.Z, Xpix, Ypix,
            st.session_state.selected_nx, st.session_state.selected_ny)

        coords = streamlit_image_coordinates(topo_img, key="topo_click")

        # Handle click
        if coords is not None:
            click_key = (coords['x'], coords['y'])
            if click_key != st.session_state.get('_last_topo_click'):
                st.session_state._last_topo_click = click_key
                nx_click = int(coords['x'] * Xpix / TOPO_DISPLAY_PX)
                ny_click = int(coords['y'] * Ypix / TOPO_DISPLAY_PX)
                nx_click = max(0, min(nx_click, Xpix - 1))
                ny_click = max(0, min(ny_click, Ypix - 1))
                select_pixel(nx_click, ny_click)
                st.rerun()

        # HTML colorbar matching image width
        st.markdown(f"""
        <div style="width:{TOPO_DISPLAY_PX}px; margin-bottom:1rem;">
          <div style="height:14px; border-radius:2px;
            background: linear-gradient(to right, #440154, #482777, #3e4989, #31688e, #26828e, #1f9e89, #35b779, #6ece58, #b5de2b, #fde725);"></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; color:#aaa; margin-top:2px;">
            <span>{z_min:.1f}</span><span>Z (nm)</span><span>{z_max:.1f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Pixel selection row
        sel_cols = st.columns([1, 1, 2])
        def _on_nx_change():
            select_pixel(int(st.session_state._nx_widget),
                         st.session_state.selected_ny)
        def _on_ny_change():
            select_pixel(st.session_state.selected_nx,
                         int(st.session_state._ny_widget))
        with sel_cols[0]:
            st.number_input(
                "X (fast)", min_value=0, max_value=Xpix - 1,
                value=st.session_state.selected_nx or 0, step=1,
                key="_nx_widget", on_change=_on_nx_change)
        with sel_cols[1]:
            st.number_input(
                "Y (slow)", min_value=0, max_value=Ypix - 1,
                value=st.session_state.selected_ny or 0, step=1,
                key="_ny_widget", on_change=_on_ny_change)
        with sel_cols[2]:
            if st.session_state.selected_nx is not None:
                z_val = st.session_state.Z[st.session_state.selected_nx,
                                           st.session_state.selected_ny]
                if not np.isnan(z_val):
                    st.metric("Z-height", f"{z_val:.2f} nm")

    # ---- F-d curves (interactive Plotly — combined subplot) ----
    with col_fd:
        st.subheader("Force-Distance Curves")

        approach = st.session_state.approach
        retract = st.session_state.retract

        if approach is not None and not approach.empty:
            nx_sel = st.session_state.selected_nx
            ny_sel = st.session_state.selected_ny
            st.caption(f"Pixel ({nx_sel}, {ny_sel})")

            fig_fd = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Approach', 'Retract'),
                shared_xaxes=True,
                vertical_spacing=0.08,
            )

            # Approach
            sep_a = approach['Separation (um)'].values * 1000
            f_a = approach['F (nN)'].values
            fig_fd.add_trace(go.Scatter(
                x=sep_a, y=f_a, mode='lines',
                line=dict(color='#1f77b4', width=1.5),
                hovertemplate='Sep: %{x:.2f} nm<br>F: %{y:.3f} nN<extra></extra>',
                showlegend=False,
            ), row=1, col=1)
            fig_fd.add_hline(y=0, line_width=0.5, line_color='gray', row=1, col=1)

            # Retract
            if retract is not None and not retract.empty:
                sep_r = retract['Separation (um)'].values * 1000
                f_r = retract['F (nN)'].values
                fig_fd.add_trace(go.Scatter(
                    x=sep_r, y=f_r, mode='lines',
                    line=dict(color='#ff7f0e', width=1.5),
                    hovertemplate='Sep: %{x:.2f} nm<br>F: %{y:.3f} nN<extra></extra>',
                    showlegend=False,
                ), row=2, col=1)
            fig_fd.add_hline(y=0, line_width=0.5, line_color='gray', row=2, col=1)

            fig_fd.update_yaxes(title_text='Force (nN)', row=1, col=1)
            fig_fd.update_yaxes(title_text='Force (nN)', row=2, col=1)
            fig_fd.update_xaxes(title_text='Separation (nm)', row=2, col=1)

            fig_fd.update_layout(
                height=520,
                margin=dict(l=45, r=10, t=25, b=30),
            )
            # Shrink subplot title font
            for ann in fig_fd.layout.annotations:
                ann.font.size = 12

            st.plotly_chart(fig_fd, use_container_width=True, key="fd_combined")
        else:
            st.info("No F-d data at this pixel. Try selecting a different one.")

else:
    # Landing page
    st.markdown("""
### Getting Started

1. **Prepare your data** — Use the Park Systems software to export your PinPoint data,
   then zip the folder of extracted CSV files.
2. **Upload** — Use the sidebar to upload the ZIP file.
3. **Explore** — View the topography map, click to inspect individual force-distance curves.
4. **Download** — Use the sidebar to export selected curves, all CSVs, or a full data package.

*Supported formats: ZIP of extracted CSVs (ppt-fd-\\*.csv files)*
    """)
