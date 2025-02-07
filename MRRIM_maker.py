#%%
#imports
import os
import tkinter as tk
from tkinter import filedialog
from osgeo import gdal, osr


#%%
# Tkinterでファイル選択
def select_file(title="Choose a file", file_types=[("Text files", "*.txt"), ("All files", "*.*")]):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
    root.destroy()
    return file_path


# 保存ファイル選択
def save_tiff_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save GeoTIFF File",
        defaultextension=".tif",
        filetypes=[("GeoTIFF Files", "*.tif")]
    )
    root.destroy()

    # `.tiff` になった場合、`.tif` に修正
    if file_path and not file_path.endswith(".tif"):
        file_path = os.path.splitext(file_path)[0] + ".tif"
    
    return file_path


#%%
# VRTファイル作成
def make_vrt(input_files, output_dir):
    output_vrt = os.path.join(output_dir, "output.vrt")

    vrt_options = gdal.BuildVRTOptions(
        resolution="average",
        separate=True,  # バンドを分離
        resampleAlg="nearest"
    )

    vrt_dataset = gdal.BuildVRT(output_vrt, input_files, options=vrt_options)

    if vrt_dataset:
        vrt_dataset.FlushCache()
        vrt_dataset = None
        print(f"VRTファイルが作成されました: {output_vrt}")
        return output_vrt
    else:
        print("エラー: VRTファイルの作成に失敗しました。")
        return None


#%%
# VRTをGeoTIFFに変換
def vrt_to_geotiff(vrt_path, output_tif):
    dataset = gdal.Open(vrt_path, gdal.GA_ReadOnly)
    if dataset is None:
        print("Error: Could not open VRT file.")
        return

    # 出力GeoTIFF設定
    driver = gdal.GetDriverByName("GTiff")
    rows, cols = dataset.RasterYSize, dataset.RasterXSize
    out_dataset = driver.Create(output_tif, cols, rows, 3, gdal.GDT_Byte)  # 8bit (0-255)

    # バンドデータ取得（バンド1, 2, 2）
    band1 = dataset.GetRasterBand(1).ReadAsArray()
    band2 = dataset.GetRasterBand(2).ReadAsArray()

    # スケーリング（1-255に正規化）
    def scale_band(band):
        return ((band - band.min()) / (band.max() - band.min()) * 254 + 1).astype('uint8')

    band1_scaled = scale_band(band1)
    band2_scaled = scale_band(band2)

    # バンド書き込み（R=1, G=2, B=2）
    out_dataset.GetRasterBand(1).WriteArray(band1_scaled)  # 赤
    out_dataset.GetRasterBand(2).WriteArray(band2_scaled)  # 緑
    out_dataset.GetRasterBand(3).WriteArray(band2_scaled)  # 青

    # CRS 設定（EPSG:6675）
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(6675)
    out_dataset.SetProjection(srs.ExportToWkt())

    # 保存
    out_dataset.FlushCache()
    out_dataset = None
    print(f"GeoTIFF successfully created: {output_tif}")


#%%
# メイン処理
def main():
    # txtファイル選択
    file1 = select_file("Select a Band1 (_1r.txt) file")
    file2 = select_file("Select a Band2 and Band3 (_2g.txt) file")

    if not file1 or not file2:
        print("エラー: ファイルが選択されていません。")
        return

    # VRT作成
    output_dir = os.path.dirname(file1)  # 最初のファイルと同じフォルダに保存
    output_vrt = make_vrt([file1, file2], output_dir)

    if not output_vrt:
        print("エラー: VRTファイルの作成に失敗しました。")
        return

    # GeoTIFF保存先選択
    output_tif = save_tiff_file()
    if not output_tif:
        print("エラー: GeoTIFFの保存場所が選択されていません。")
        return

    # GeoTIFF作成
    vrt_to_geotiff(output_vrt, output_tif)


#%%
if __name__ == "__main__":
    main()
