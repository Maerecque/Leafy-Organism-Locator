# Leafy Organism Locator: GU edition
This code is used to make a map (raster TIFF file) of all high vegatation found in a certain area. This repo is made for users within my team to download their own version of a code to run locally.

## Instructions
Follow the instructions below to use the code:

1. Find a CIR photo or a photo of an area with at least a red and infrared band. Also find a DTM and DSM map for the area.
2. Use QGIS to create an MSAVI map of this area. *Don't run nb01_create_green_index.py since it doesn't work ***yet***.*
3. Run the code from `nb02_fill_dtm_gaps.py` on the DTM **and the DSM**.
4. Run the code from `nb03_calc_relative_height.py`.
5. *It may be that the resolution of the aerial photo differs from the height model. If this is the case, correct it with QGIS. or use GDAL if you have access to it.*
6. Run the code from `nb04_calc_relative_vegatation_height.py`.

## Findings So Far
The code from `/lib/nb01_create_green_index.py` to create an MSAVI map does not work. **Solution:** A spatial model has been set up for QGIS to create an MSAVI map from a CIR map. One advantage of this is that these MSAVI maps can be created in bulk with QGIS.