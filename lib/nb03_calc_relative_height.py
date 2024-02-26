import rasterio
import numpy as np
import tkinter.filedialog
import tkinter as tk


def calc_relative_height(dtm_file: str, dsm_file: str, output_file: str, new_nodata_value: int = -9999) -> None:
    """Calculate relative height and save it to a new raster file.

    This function reads a DTM raster and a DSM raster, calculates the relative height, and saves the result to a new raster file.

    Args:
        dtm_file (str): Location of the DTM raster file.
        dsm_file (str): Location of the DSM raster file.
        output_file (str): Destination location of the raster image with the result of the relative height.
        new_nodata_value (int, optional): Value that will be used to replace the NODATA values. Defaults to -9999.
    """
    # Check if a DTM file, DSM file, and output location was provided
    if not all([dtm_file, dsm_file, output_file]):
        raise ValueError("Please provide a path to the DTM file, a path to the DSM file, and an output location.")

    # Open the DTM file
    with rasterio.open(dtm_file) as dtm:
        # Read the first band of the DTM file
        dtm_data = dtm.read(1)

    # Open the DSM file
    with rasterio.open(dsm_file) as dsm:
        # Read the first band of the DSM file
        dsm_data = dsm.read(1)

        # Get the profile of the DSM file
        dsm_profile = dsm.profile.copy()
        dsm_profile.update(dtype=rasterio.float32, count=1)

    # On some place the DTM will have a nodata value of -9999, but the DSM will have something greater than 0. This can be a tree above water for example. # noqa: E501
    # therefore I changed the code on line 41 from:
    # dtm_data > new_nodata_value,
    # to
    # dsm_data > new_nodata_value,

    # Calculate the relative height
    relative_height = np.where(
        dsm_data > new_nodata_value,
        dsm_data.astype(float) - dtm_data.astype(float),
        new_nodata_value
    )

    # Write the relative height to the output location
    with rasterio.open(output_file, 'w', **dsm_profile) as dst:
        dst.write(relative_height.astype(rasterio.float32), 1)

    # Print a message indicating that the relative height was calculated and saved
    print(f"Relative height saved at {output_file}")


if __name__ == "__main__":
    # Create a tkinter window to select the DTM file, the DSM file, and the output location
    root = tk.Tk()
    root.withdraw()
    dtm_file = tk.filedialog.askopenfilename(title="Select the DTM file", filetypes=[("TIF", "*.tif *.tiff")], multiple=False)
    dsm_file = tk.filedialog.askopenfilename(title="Select the DSM file", filetypes=[("TIF", "*.tif *.tiff")], multiple=False)
    output_file = tk.filedialog.asksaveasfilename(title="Select the output location", filetypes=[("TIF", "*.tif *.tiff")])

    calc_relative_height(dtm_file, dsm_file, output_file)
