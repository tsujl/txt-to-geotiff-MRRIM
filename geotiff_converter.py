#%%
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from osgeo import gdal, osr
import numpy as np


# GUIでファイルを選択
def select_file(title="Choose a file", file_types=[("Text files", "*.txt"), ("All files", "*.*")]):
    file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
    return file_path


# 出力ファイル選択（.tif）
def save_tiff_file():
    file_path = filedialog.asksaveasfilename(
        title="Save GeoTIFF File",
        defaultextension=".tif",
        filetypes=[("GeoTIFF Files", "*.tif")]
    )
    if file_path and not file_path.endswith(".tif"):
        file_path = os.path.splitext(file_path)[0] + ".tif"
    return file_path


# VRTファイル作成（QGISの設定と一致）
def make_vrt(input_files, output_dir):
    output_vrt = os.path.join(output_dir, "output.vrt")

    vrt_options = gdal.BuildVRTOptions(
        separate=True,
        resampleAlg="nearest",
        resolution="highest",
        addAlpha=False,
        srcNodata=""
    )

    vrt_dataset = gdal.BuildVRT(output_vrt, input_files, options=vrt_options)
    if vrt_dataset:
        vrt_dataset.FlushCache()
        vrt_dataset = None
        return output_vrt
    return None


# 座標情報を `.txt` から取得
def extract_georeference(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    geo_info = {}
    for line in lines[:6]:  # 最初の数行に座標データがある
        parts = line.strip().split()
        if len(parts) == 2:
            key, value = parts
            geo_info[key.lower()] = float(value)

    if all(k in geo_info for k in ("xllcorner", "yllcorner", "cellsize")):
        return geo_info
    return None


# VRTをGeoTIFFに変換
def vrt_to_geotiff(vrt_path, output_tif, ref_txt):
    dataset = gdal.Open(vrt_path, gdal.GA_ReadOnly)
    if dataset is None:
        return False

    driver = gdal.GetDriverByName("GTiff")
    rows, cols = dataset.RasterYSize, dataset.RasterXSize
    out_dataset = driver.Create(output_tif, cols, rows, 3, gdal.GDT_Byte)

    geo_info = extract_georeference(ref_txt)
    if geo_info:
        xll, yll, cellsize = geo_info["xllcorner"], geo_info["yllcorner"], geo_info["cellsize"]
        transform = (xll, cellsize, 0, yll + rows * cellsize, 0, -cellsize)
        out_dataset.SetGeoTransform(transform)

    # バンド情報（赤:1, 緑:2, 青:2）
    band1 = dataset.GetRasterBand(1).ReadAsArray()
    band2 = dataset.GetRasterBand(2).ReadAsArray()

    band1[band1 == -9999] = 0
    band2[band2 == -9999] = 0

    # スケーリング処理（1-255範囲に調整）
    def scale_band(band):
        return ((band - band.min()) / (band.max() - band.min()) * 254 + 1).astype('uint8')

    band1_scaled = scale_band(band1)
    band2_scaled = scale_band(band2)

    out_dataset.GetRasterBand(1).WriteArray(band1_scaled)
    out_dataset.GetRasterBand(2).WriteArray(band2_scaled)
    out_dataset.GetRasterBand(3).WriteArray(band2_scaled)

    out_dataset.GetRasterBand(1).SetNoDataValue(0)
    out_dataset.GetRasterBand(2).SetNoDataValue(0)
    out_dataset.GetRasterBand(3).SetNoDataValue(0)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(6675)
    out_dataset.SetProjection(srs.ExportToWkt())

    out_dataset.FlushCache()
    out_dataset = None
    return True


# Tkinter GUI のウィンドウを作成
def create_gui():
    root = tk.Tk()
    root.title("GeoTIFF Converter")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    tk.Label(frame, text="Select Input Files:").pack()

    file1_label = tk.Label(frame, text="Band1: Not Selected")
    file1_label.pack()

    file2_label = tk.Label(frame, text="Band2: Not Selected")
    file2_label.pack()

    file1 = None
    file2 = None

    def select_file1():
        nonlocal file1
        file1 = select_file("Select a Band1 (_1r.txt) file")
        if file1:
            file1_label.config(text=f"Band1: {os.path.basename(file1)}")

    def select_file2():
        nonlocal file2
        file2 = select_file("Select a Band2 and Band3 (_2g.txt) file")
        if file2:
            file2_label.config(text=f"Band2: {os.path.basename(file2)}")

    tk.Button(frame, text="Select Band1 (_1r.txt)", command=select_file1).pack()
    tk.Button(frame, text="Select Band2 (_2g.txt)", command=select_file2).pack()

    def process():
        if not file1 or not file2:
            messagebox.showerror("Error", "Please select both input files!")
            return

        output_tif = save_tiff_file()
        if not output_tif:
            messagebox.showerror("Error", "Output file not selected!")
            return

        output_dir = os.path.dirname(output_tif)
        output_vrt = make_vrt([file1, file2], output_dir)

        if not output_vrt:
            messagebox.showerror("Error", "Failed to create VRT file!")
            return

        success = vrt_to_geotiff(output_vrt, output_tif, file1)
        if success:
            os.remove(output_vrt)
            messagebox.showinfo("Success", f"GeoTIFF created: {output_tif}")
        else:
            messagebox.showerror("Error", "Failed to create GeoTIFF!")

    tk.Button(frame, text="Convert to GeoTIFF", command=process).pack()
    root.mainloop()

#%%
# メイン処理
if __name__ == "__main__":
    create_gui()
