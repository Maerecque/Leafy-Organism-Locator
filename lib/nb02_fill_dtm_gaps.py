import rasterio
from rasterio._fill import _fillnodata as fillnodata
import tkinter.filedialog
import tkinter as tk


def fillDtmGaps(dtm_file: str, output_file: str, new_nodata_value: int = -9999):
    """Fill gaps in  a DTM file. This function will also work on DSM files.

    Sources:
        https://mapscaping.com/a-guide-to-nodata-values-in-rasters-with-python/
        https://pygis.io/docs/e_raster_replace_values.html

    Args:
        dtm_file (str): Path to the DTM file.
        output_file (str): Path to the output file.
        new_nodata_value (int, optional): New NODATA value. Defaults to -9999.
    """
    # Check if a DTM file and output location was provided
    if not all([dtm_file, output_file]):
        raise ValueError("Please provide a path to the DTM file and an output location.")

    # Open the DTM file
    with rasterio.open(dtm_file) as dtm:
        # Read the first band of the DTM file
        dtm_data = dtm.read(1)

        # Get the profile of the DTM file
        dtm_profile = dtm.profile.copy()

        # Update the data type, NODATA value, and count of the DTM profile
        dtm_profile.update(dtype=rasterio.float32, nodata=new_nodata_value, count=1)

        # Creata a boolean mask of the DTM data with every value above 1000
        # The reason 1000 is chosen is because the DTM data is in meters and the highest point in the Netherlands is 322.7 meters
        # So any value above 1000 is most likely a NODATA value
        mask_boolean = dtm_data > 1000

        # Change every value above 1000 to the NODATA value
        dtm_data[mask_boolean] = new_nodata_value

        # Fill the NODATA values
        filled = fillnodata(dtm_data, mask=mask_boolean, max_search_distance=1, smoothing_iterations=0)

    # Write the filled DTM to the output location
    with rasterio.open(output_file, 'w', compress="DEFLATE", predictor=2, zlevel=9, **dtm_profile) as dst:
        dst.write(filled.astype(rasterio.float32), 1)

    # Print a message indicating that the DTM was filled and saved
    print(f"Filled DTM saved at {output_location}")


if __name__ == "__main__":
    # Create a tkinter window to select the DTM file and the output location
    root = tk.Tk()
    root.withdraw()
    dtm_file = tk.filedialog.askopenfilename(title="Select the DTM file", filetypes=[("TIF", "*.tif *.tiff")], multiple=False)
    output_location = tk.filedialog.asksaveasfilename(title="Select the output location", filetypes=[("TIF", "*.tif *.tiff")])

    fillDtmGaps(dtm_file, output_location)
