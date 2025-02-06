#%%
#imports
import sys
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from osgeo import gdal, osr, ogr 

# %%
#get_file_path
def select_file(title="Choose files(_1r, _2g)"):
    root = tk.TK()
    root.withdraw()
    root.attributes("-topmost", True)
    root.focus_force()
    file_path = filedialog.askopenfilename(title=title, filetypes=[(".txt files", "*.txt"), ("All files", "*.*")])
    return file_path
#%%
#save_file
def save_file(title="Save GeoTIFF"):
    root = tk.TK()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=".txt",
        filetypes=[("GeoTIFF Files")]
    )
    return file_path
#load
def load_dem_data(file_path):
    return np.loadtxt(file_path)
#%%
#create geoTIFF
def create_geotiff(output_tif, band1_data, band2_data, band3_data):
    rows, cols = band1_data.shape
    drive = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(output_tif, cols, rows, 3, gdal.GDT_Float32)

    for i, band_data in enumerate([band1_data, band2_data, band3_data], start = 1):
        band = dataset.GetRasterBand(i)
        band.WriteArray(band_data)

        min_val, max_val = np.min(band_data), np.max(band_data)
        band.SetNoDataValue(min_val)
        band.SetNoDataValue(max_val)

    
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
    
    
#%%
if __name__ == "__main__":
    main()