import numpy as np
import rasterio
import tkinter.filedialog
import tkinter as tk


def create_msavi(cir_file: str, output_file: str) -> None:
    """Creates a green index out of a CIR image. The index that is used is the msavi.

    Note: The Index seems to be calculated correctly, but the values are not correct.
    As a solution a spatial model for QGIS is made, which calculates the index correctly.
    The use of QGIS allows to make MSAVI maps in bulk.
    *TLDR: Use the QGIS model instead of this function.*

    Args:
        cir_file (str): Path to the CIR image.
        output_file (str): Path to the output file.
    """
    # Check if a cir file and output location was provided
    if not all([cir_file, output_file]):
        raise ValueError("Please provide a path to the CIR image and an output location.")

    # Open the CIR
    with rasterio.open(cir_file) as cir:
        cir_data = cir.read()

        # Get the profile of the CIR file
        cir_profile = cir.profile.copy()

    # Check if the profile has a photometric key that is ycbcr and if so, change it to grayscale 1 band
    if cir_profile["photometric"] == "ycbcr":
        cir_profile["photometric"] = 1

    # Create the msavi index
    msavi = (2 * cir_data[1] + 1 - np.sqrt((2 * cir_data[1] + 1)**2 - 8 * (cir_data[1] - cir_data[0]))) / 2

    # Write the msavi index to the output file
    with rasterio.open(output_file, 'w', **cir_profile) as dst:
        dst.write(msavi.astype(rasterio.float32), 1)

    # Print a message indicating that the msavi index was created
    print(f"Created msavi index at {output_file}")


if __name__ == "__main__":
    # Create a tkinter window to select the CIR image and the output location
    root = tk.Tk()
    root.withdraw()
    cir_file = tk.filedialog.askopenfilename(title="Select the CIR image", filetypes=[("TIF", "*.tif *.tiff")], multiple=False)
    output_file = tk.filedialog.asksaveasfilename(title="Select the output location", filetypes=[("TIF", "*.tif *.tiff")])

    create_msavi(cir_file, output_file)
