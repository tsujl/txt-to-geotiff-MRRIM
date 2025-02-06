#%%
#imports
import sys
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from osgeo import gdal, osr, ogr , gdal_array


# %%
#get_file_path
def select_file(title="Choose files(_1r, _2g)"):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.focus_force()
    file_path = filedialog.askopenfilename(title=title, filetypes=[(".txt files", "*.txt"), ("All files", "*.*")])
    return file_path


#%%
#save_file
def save_file(title="Save GeoTIFF"):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=".txt",
        filetypes=[("GeoTIFF Files", "*.tif")]
    )
    return file_path


#load
def load_dem_data(file_path):
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"Error: Could not open {file_path}")
        return None
    return dataset.GetRasterBand(1).ReadAsArray()

#%%
#scaling 1-255
def scale_band(band_data):
    """バンドデータを1と255の範囲にスケーリング"""
    min_val, max_val = np.min(band_data), np.max(band_data)
    scaled_data = 1 + ((band_data - min_val) * (255 - 1)) / (max_val - min_val)
    return scaled_data

#%%
#create geoTIFF
def create_geotiff(output_tif, band1_data, band2_data, band3_data):
    rows, cols = band1_data.shape
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(output_tif, cols, rows, 3, gdal.GDT_Float32)

    band1_data = scale_band(band1_data)
    band2_data = scale_band(band2_data)
    band3_data = scale_band(band3_data)

    for i, band_data in enumerate([band1_data, band2_data, band3_data], start = 1):
        band = dataset.GetRasterBand(i)
        band.WriteArray(band_data)

    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(6675)
    dataset.SetProjection(srs.ExportToWkt())
    dataset = None #save


#%%
#main
def main():
    file1 = select_file("Select a Band1(_1r.txt) file")
    file2 = select_file("Select a Band2 and band3(_2g.txt) file")

    if not file1 or not file2:
        print("Error: File selection was cancelled.")
        return
    
    output_tif = save_file("Save as .tif")

    if not output_tif:
        print("Error: Enter output file name")
        return
    
    band1_data = load_dem_data(file1)
    band2_data = load_dem_data(file2)
    band3_data = load_dem_data(file2) #same as band2

    create_geotiff(output_tif, band1_data, band2_data, band3_data)
    
    if os.path.exists(output_tif):
        print(f"GeoTIFF '{output_tif}' が作成されました。")
    else:
        print("Error: GeoTIFF ファイルの作成に失敗しました。")
        
#%%
if __name__ == "__main__":
    main()