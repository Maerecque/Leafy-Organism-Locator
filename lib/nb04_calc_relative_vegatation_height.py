import numpy as np
import rasterio
import tkinter.filedialog as tkfd
import tkinter as tk
import os


def rasters_to_tuple(msavi_file: str, rel_height_file: str, new_nodata_value: int = -9999) -> tuple:
    """Reads two raster files and returns them as a tuple.

    Args:
        msavi_file (str): Path to the msavi raster file.
        rel_height_file (str): Path to the relative height raster file.
        new_nodata_value (int, optional): Value that will be used to replace the NODATA values. Defaults to -9999.

    Returns:
        tuple: Tuple containing the msavi raster and the relative height raster.
    """
    # Check if a msavi file and a relative height file was provided
    if not all([msavi_file, rel_height_file]):
        raise ValueError("Please provide a path to the msavi file and a path to the relative height file.")

    # Read the msavi raster
    with rasterio.open(msavi_file) as msavi:
        msavi_data = msavi.read(1)

        # Get the profile of the msavi file
        msavi_profile = msavi.profile.copy()
        msavi_profile.update(nodata=new_nodata_value)

        # Replace the current NODATA values with the new NODATA value
        msavi_data[msavi_data == msavi.nodata] = new_nodata_value

    # Read the relative height raster
    with rasterio.open(rel_height_file) as rel_height:
        rel_height_data = rel_height.read(1)

        # Get the profile of the relative height file
        rel_height_profile = rel_height.profile.copy()
        rel_height_profile.update(nodata=new_nodata_value)

        # Replace the current NODATA values with the new NODATA value
        rel_height_data[rel_height_data == rel_height.nodata] = new_nodata_value

    # Return the msavi raster and the relative height raster as a tuple
    return msavi_data, rel_height_data, msavi.meta


def resample_heightraster(input_height_raster: str, output_height_raster: str, resolution: float = 0.25, new_nodata_value: int = -9999) -> None:  # noqa: E501
    """Resamples a height raster to a resolution of 0.25m or another resolution if specified.

    NOTE: GDAL must be installed on the system for this function to work. GDAL is not included in GU environment.

    Args:
        input_height_raster (str): Path to the input height raster.
        output_height_raster (str): Path to the output height raster.
        resolution (float, optional): Resolution of the output height raster in meters. Defaults to 0.25.
        new_nodata_value (int, optional): Value that will be used to replace the NODATA values. Defaults to -9999.
    """
    # Define GDAL command for resampling
    gdal_command = f"gdalwarp -overwrite -dstnodata {new_nodata_value} {input_height_raster} -r near -tr {resolution} {resolution} -co compress='DEFLATE' -co predictor=2 -co zlevel=9 {output_height_raster}"  # noqa: E501

    # Execute GDAL command and print the output
    print(os.popen(gdal_command).read())


def clip_raster(input_raster: np.ndarray, shape_diff: tuple):
    """Clips a raster by removing the first and last row and column.

    This was done to remove the black border that was created by the stitching of the images.

    Args:
        input_raster (np.ndarray): Numpy array of the raster to clip.
        shape_diff (tuple): Difference in shape between the msavi raster and the relative height raster.

    Returns:
        np.ndarray: Clipped raster.
    """
    if shape_diff[0] == 1 and shape_diff[1] == 1:
        # Remove the last row
        clipped_raster = np.delete(input_raster, input_raster.shape[0] - 1, axis=0)

        # Remove the last column
        clipped_raster = np.delete(clipped_raster, clipped_raster.shape[1] - 1, axis=1)

    if shape_diff[0] == 2 and shape_diff[1] == 2:
        # Remove the first and last row
        clipped_raster = np.delete(input_raster, [0, input_raster.shape[0] - 1], axis=0)

        # Remove the first and last column
        clipped_raster = np.delete(clipped_raster, [0, clipped_raster.shape[1] - 1], axis=1)

    # Return the clipped raster
    return clipped_raster


def calc_veg_height(green_index_raster: np.ndarray, rel_height: np.ndarray, new_nodata_value: int = -9999) -> np.ndarray:
    """Calculates the relative vegetation height.

    Args:
        green_index_raster (np.ndarray): Numpy array of the green_index_raster raster.
        rel_height (np.ndarray): Numpy array of the relative height raster.
        new_nodata_value (int, optional): Value that will be used to replace the NODATA values. Defaults to -9999.

    Returns:
        np.ndarray: Numpy array of the vegetation height raster.
    """
    # Derive green (1) and non-green (nan) pixels from the msavi raster
    green_pixels = np.where(green_index_raster >= 0, 1, np.nan)

    # Extract height values and where available replace the nodata value with nan
    height = np.where(rel_height > new_nodata_value, rel_height, np.nan)

    # Calculate the vegetation height
    veg_height = green_pixels * height

    print("Veg height: ", veg_height)

    # Return the vegetation height
    return veg_height


def calc_high_veg(green_index_raster: np.ndarray, rel_height: np.ndarray, new_nodata_value: int = -9999, min_veg_height: int = 2) -> np.ndarray:  # noqa: E501
    """Creates a raster with the high vegetation.

    Args:
        green_index_raster (np.ndarray): Numpy array of the green_index_raster raster.
        rel_height (np.ndarray): Numpy array of the relative height raster.
        new_nodata_value (int, optional): Value that will be used to replace the NODATA values. Defaults to -9999.
        min_veg_height (int, optional): Minimum vegetation height. Defaults to 2.

    Returns:
        np.ndarray: Numpy array of the vegetation height raster.
    """
    # Derive green (1) and non-green (nan) pixels from the msavi raster
    green_pixels = np.where(green_index_raster >= 0.3, green_index_raster, np.nan)

    # Extract height values and where available replace the nodata value with nan
    height = np.where(rel_height > min_veg_height, 1, np.nan)

    # Calculate the vegetation height
    veg_height = green_pixels * height

    # Overwrite any value that is not a number with the new_nodata_value
    veg_height = np.where(np.isnan(veg_height), new_nodata_value, veg_height)

    print("Veg height: ", veg_height)

    # Return the vegetation height
    return veg_height


def write_raster(raster_array: np.ndarray, meta: dict, output_file: str) -> None:
    """Writes a raster to a file.

    Args:
        raster_array (np.ndarray): Numpy array of the raster.
        meta (dict): Metadata of the raster.
        output_file (str): Path to the output file.
    """
    # Check if an output file was provided
    if not output_file:
        raise ValueError("Please provide an output location.")

    # Set spatial characteristics of the output object to mirror the input
    kwargs = meta.copy()
    kwargs.update(dtype=rasterio.float32, count=1)

    # Write the raster to the output file
    with rasterio.open(output_file, 'w', compress='DEFLATE', predictor=2, zlevel=9, **meta) as dst:
        dst.write_band(1, raster_array.astype(rasterio.float32))

    # Print a message indicating that the raster was written to the output file
    print(f"Raster saved at {output_file}")


if __name__ == "__main__":
    # Create a tkinter window to select the msavi raster, the relative height raster, and the output location
    root = tk.Tk()
    root.withdraw()
    msavi_file = tkfd.askopenfilename(title="Select the msavi raster", filetypes=[("TIF", "*.tif *.tiff")], multiple=False)
    rel_height_file = tkfd.askopenfilename(title="Select the relative height raster", filetypes=[("TIF", "*.tif *.tiff")], multiple=False)  # noqa: E501
    # rel_height_output_file = tkfd.asksaveasfilename(title="Select the output location for the relative height raster", filetypes=[("TIF", "*.tif *.tiff")])  # noqa: E501
    output_file = tkfd.asksaveasfilename(title="Select the output location", filetypes=[("TIF", "*.tif *.tiff")])

    # # Resample the relative height raster
    # # This is commented out because we can't use GDAL in the GU environment
    # # Solution is done in QGIS see: https://gis.stackexchange.com/questions/73046/resampling-geotiff-images-to-same-resolution-using-qgis#:~:text=Using%20GDAL_Warp%20%2D%20this,point%20of%20view!).  # noqa: E501
    # resample_heightraster(rel_height_file, rel_height_output_file)

    # Import the msavi raster and the relative height raster
    msavi, rel_height, meta = rasters_to_tuple(msavi_file, rel_height_file)

    # CHeck if the resolution of the msavi raster is the same as the relative height raster
    if msavi.shape != rel_height.shape:
        shape_diff = (msavi.shape[0] - rel_height.shape[0], msavi.shape[1] - rel_height.shape[1])
        # Clip the msavi raster
        msavi = clip_raster(msavi, shape_diff)
        print("Clipped msavi raster")

    # Calculate the relative vegetation height
    relative_veg_height = calc_high_veg(msavi, rel_height)

    # Write the relative vegetation height to the output file
    write_raster(relative_veg_height, meta, output_file)

    # # Clean up the temporary relative height raster
    # os.remove(rel_height_output_file)
