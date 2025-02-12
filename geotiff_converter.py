#%%
import os
from osgeo import gdal, osr

def make_vrt(input_files, output_vrt):
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

def vrt_to_geotiff(vrt_path, output_tif):
    dataset = gdal.Open(vrt_path, gdal.GA_ReadOnly)
    if dataset is None:
        return False

    driver = gdal.GetDriverByName("GTiff")
    rows, cols = dataset.RasterYSize, dataset.RasterXSize
    out_dataset = driver.Create(output_tif, cols, rows, 3, gdal.GDT_Byte)

    band1 = dataset.GetRasterBand(1).ReadAsArray()
    band2 = dataset.GetRasterBand(2).ReadAsArray()

    band1[band1 == -9999] = 0
    band2[band2 == -9999] = 0

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

def process_directory(directory):
    file_sets = {
        "mrrim": ["mrrim_1r.txt", "mrrim_2g.txt"],
        "smrrim_le": ["smrrim_le_1r.txt", "smrrim_le_2g.txt"],
        "smrrim_ri": ["smrrim_ri_1r.txt", "smrrim_ri_2g.txt"]
    }
    
    for name, files in file_sets.items():
        input_files = [os.path.join(directory, f) for f in files]
        output_vrt = os.path.join(directory, f"{name}.vrt")
        output_tif = os.path.join(directory, f"{name}.tif")
        
        vrt_path = make_vrt(input_files, output_vrt)
        if vrt_path:
            success = vrt_to_geotiff(vrt_path, output_tif)
            os.remove(output_vrt)
            print(f"Processed {output_tif}: {'Success' if success else 'Failed'}")
        else:
            print(f"Failed to create VRT for {name}")

if __name__ == "__main__":
    process_directory(os.getcwd())
