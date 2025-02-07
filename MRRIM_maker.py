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
    dataset = gdal.Open(file_path, gdal.GA_Update)
    if dataset is None:
        print(f"Error: Could not open {file_path}")
        return None
    return dataset.GetRasterBand(1).ReadAsArray()

#%%
def make_vrt(input_files):
    vrt_options = gdal.BuildVRTOptions(
        resolution="average",
        separate="True",
        resampleAlg="nearest",
        overwrite=True
    )
    
    output_vrt = os.path.join(file_path, "output.vrt")

    #make VRT
    vrt_dataset = gdal.BuildVRT(output_vrt, input_files, vrt_options=vrt_options)

    if vrt_dataset:
        vrt_dataset = None
        return output_vrt
    else:
        return None
    
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
    
    input_files = [file1, file2]
    make_vrt(input_files)
   
#%%
if __name__ == "__main__":
    main()