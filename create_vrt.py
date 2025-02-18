#%%
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from osgeo import gdal

def select_file(title="Select a file"):
    file_path = filedialog.askopenfilename(title=title, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    return file_path

def save_vrt_file():
    file_path = filedialog.asksaveasfilename(
        title="Save VRT File",
        defaultextension=".vrt",
        filetypes=[("VRT Files", "*.vrt")]
    )
    return file_path

def make_vrt(input_files, output_vrt):
    vrt_options = gdal.BuildVRTOptions(separate=True)
    vrt_dataset = gdal.BuildVRT(output_vrt, input_files, options=vrt_options)
    if vrt_dataset:
        vrt_dataset.FlushCache()
        vrt_dataset = None
        return True
    return False

def create_vrt():
    file1 = select_file("Select Band1 (_1r.txt) file")
    if not file1:
        messagebox.showerror("Error", "Band1 file not selected!")
        return
    
    file2 = select_file("Select Band2 (_2g.txt) file")
    if not file2:
        messagebox.showerror("Error", "Band2 file not selected!")
        return
    
    output_vrt = save_vrt_file()
    if not output_vrt:
        messagebox.showerror("Error", "Output VRT file not selected!")
        return
    
    success = make_vrt([file1, file2], output_vrt)
    if success:
        messagebox.showinfo("Success", f"VRT file created: {output_vrt}")
    else:
        messagebox.showerror("Error", "Failed to create VRT file!")

def create_gui():
    root = tk.Tk()
    root.title("VRT Creator")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    tk.Button(frame, text="Create VRT", command=create_vrt).pack()
    root.mainloop()

if __name__ == "__main__":
    create_gui()