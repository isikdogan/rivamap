# RivaMap: An Automated River Analysis and Mapping Engine

## Related papers
* F. Isikdogan, A.C. Bovik, and P. Passalacqua, "RivaMap: an automated river analysis and mapping engine," *Remote Sensing of Environment, Special Issue on Big Remotely Sensed Data*, 2017. [[**Read at ScienceDirect**]](http://www.sciencedirect.com/science/article/pii/S0034425717301475), [[**PDF**]](http://www.isikdogan.com/files/isikdogan2017_rivamap.pdf)
* F. Isikdogan, A.C. Bovik, and P. Passalacqua, "Automatic channel network extraction from remotely sensed images by singularity analysis," *IEEE Geoscience and Remote Sensing Letters*, 12, 11, 2218-2221, 2015. [[**Read at IEEExplore**]](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=7192616), [[**PDF**]](http://live.ece.utexas.edu/publications/2015/Isikdogan_GRSL_2015_Channel_Network_Extraction.pdf)

## Dependencies and Installation
**Dependencies:**
* OpenCV 2.4
* Python 2.7
* Numpy
* Scipy
* Matplotlib
* GDAL
* pyshp

**Installing from PyPI:**

    $ sudo pip install rivamap

**Installing from GitHub:**

    $ git clone https://github.com/isikdogan/rivamap.git
    $ sudo python setup.py install

**Example Use:**

See [example.ipynb](./examples/example.ipynb)

## Example Results

<a href="http://live.ece.utexas.edu/research/rivamap/img/keithsburg.png"><img src="http://live.ece.utexas.edu/research/rivamap/img/keithsburg.png" alt="Example Result" height="250"></a>
<a href="http://live.ece.utexas.edu/research/rivamap/img/waxlake.png"><img src="http://live.ece.utexas.edu/research/rivamap/img/waxlake.png" alt="Example Result" height="250"></a>
<a href="http://live.ece.utexas.edu/research/rivamap/img/mississippi.png"><img src="http://live.ece.utexas.edu/research/rivamap/img/mississippi.png" alt="Example Result" height="250"></a>
<a href="http://live.ece.utexas.edu/research/rivamap/img/ganges.png"><img src="http://live.ece.utexas.edu/research/rivamap/img/ganges.png" alt="Example Result" height="250"></a>

## Reference

<table>
    <tbody>
        <tr>
            <th>
                <p>
                    Function
                </p>
            </th>
            <th>
                <p>
                    Description
                </p>
            </th>
        </tr>
        <tr>
            <td>
                <p>
                    preprocess.mndwi
                </p>
            </td>
            <td>
                <p>
                    Computes the modified normalized difference water index.
                </p>
                <p>
                     Inputs:
                    <br/>
                     green: green band (e.g. Landsat 8 band 3)<br/>
                     mir: middle infrared band (e.g. Landsat 8 band 6)
                </p>
                <p>
                     Returns:
                    <br/>
                     mndwi: mndwi response
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    preprocess.contrastStretch
                </p>
            </td>
            <td>
                <p>
                    Applies contrast stretch to an input image. Inputs and outputs an image.
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    preprocess.im2double
                </p>
            </td>
            <td>
                <p>
                    Converts image datatype to float. Inputs and outputs an image.
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    preprocess.double2im
                </p>
            </td>
            <td>
                <p>
                    Converts double data array to image. Inputs and outputs an image.
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    singularity_index.SingularityIndexFilters
                </p>
            </td>
            <td>
                <p>
                    Creates the filters that are needed for computing the modified multiscale singularity index response. The filters can be used for processing many input images once the filters are created.
                </p>
                <p>
                    Keyword arguments:<br/>
                    minScale: minimum scale sigma (default 1.2 pixels)<br/>
                    nrScales: number of scales (default 15)
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    singularity_index.applyMMSI
                </p>
            </td>
            <td>
                <p>
                    Applies the filters to a given input image to compute the modified multiscale singularity index response. Estimates the width and the dominant orientation angle for each spatial location.
                </p>
                <p>
                    Inputs:<br/>
                    I1: input image (e.g. Landsat NIR band or MNDWI)<br/>
                    filters: an instance of SingularityIndexFilters class that contains precomputed filters<br/>
                    togglePolarity: changes polarity, use if the rivers are darker than land in the input image (i.e. SAR images)
                </p>
                <p>
                    Returns:<br/>
                    psi: the singularity index response<br/>
                    widthMap: estimated width at each spatial location (x,y)<br/>
                    orient: local orientation at each spatial location (x,y)
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    delineate.extractCenterlines
                </p>
            </td>
            <td>
                <p>
                    Uses the previously computed singularity index response (psi) and the dominant orientation (orient) to extract centerlines.
                </p>
                <p>
                    Inputs: (can be obtained by running applyMMSI function)<br/>
                    psi: the singularity index response<br/>
                    orient: local orientation at each spatial location (x,y)
                </p>
                <p>
                    Returns:<br/>
                    nms: Non-maxima suppressed singularity index response (centerlines)
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    delineate.thresholdCenterlines
                </p>
            </td>
            <td>
                <p>
                    Uses a continuity-preserving hysteresis thresholding to classify centerlines.
                </p>
                <p>
                    Inputs:<br/>
                    nms: Non-maxima suppressed singularity index response
                </p>
                <p>
                    Keyword Arguments:<br/>
                    bimodal: true if the areas of rivers in the image are sufficiently large that the distribution of psi is bimodal<br/>
                    tLow: lower threshold (automatically set if bimodal=True)<br/>
                    tHigh: higher threshold (automatically set if bimodal=True)
                </p>
                <p>
                    Returns:<br/>
                    centerlines: a binary matrix that indicates centerline locations
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    georef.loadGeoMetadata
                </p>
            </td>
            <td>
                <p>
                    Reads metadata from a GeoTIFF file.
                </p>
                <p>
                    Inputs:<br/>
                    filepath: the path to the file
                </p>
                <p>
                    Returns:<br/>
                    gm: metadata
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    georef.saveAsGeoTiff
                </p>
            </td>
            <td>
                <p>
                    Saves a raster image as a GeoTIFF file
                </p>
                <p>
                    Inputs:<br/>
                    gm: georeferencing metadata<br/>
                    I: raster image<br/>
                    filepath: save destination
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    georef.pix2lonlat
                </p>
            </td>
            <td>
                <p>
                    Convers pixel coordinates into longitude and latitude.
                </p>
                <p>
                    Inputs:<br/>
                    gm: georeferencing metadata<br/>
                    x, y: pixel coordinates
                </p>
                <p>
                    Returns:<br/>
                    lon, lat: longitude and latitude
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    georef.lonlat2pix
                </p>
            </td>
            <td>
                <p>
                    Convers longitude and latitude into pixel coordinates.
                </p>
                <p>
                    Inputs:<br/>
                    gm: georeferencing metadata<br/>
                    lon, lat: longitude and latitude
                </p>
                <p>
                    Returns:<br/>
                    x, y: pixel coordinates
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    georef.exportCSVfile
                </p>
            </td>
            <td>
                <p>
                    Exports (coordinate, width) pairs to a comma separated text file.
                </p>
                <p>
                    Inputs:<br/>
                    centerlines: a binary matrix that indicates centerline locations<br/>
                    widthMap: estimated width at each spatial location (x,y)<br/>
                    gm: georeferencing metadata filepath: the path to the file
                </p>
            </td>
        </tr>
	<tr>
            <td>
                <p>
                    georef.exportShapeFile [NEW]
                </p>
            </td>
            <td>
                <p>
                    Exports line segments to a ShapeFile.
                </p>
                <p>
                    Inputs:<br/>
                    centerlines: a binary matrix that indicates centerline locations<br/>
                    widthMap: estimated width at each spatial location (x,y)<br/>
                    gm: georeferencing metadata filepath: the path to the file
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    visualization.generateRasterMap
                </p>
            </td>
            <td>
                <p>
                    Generates a raster map of channels. It draws a line of length w(x, y) and orientation &theta;(x, y) at each spatial location.
                </p>
                <p>
                    Inputs:<br/>
                    centerlines: a binary matrix that indicates centerline locations<br/>
                    orient: local orientation at each spatial location (x,y)<br/>
                    widthMap: estimated width at each spatial location (x,y)
                </p>
                <p>
                    Keyword Arguments:<br/>
                    thickness: thickness of the lines (default 3)
                </p>
                <p>
                    Returns:<br/>
                    raster: the raster map
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    visualization.generateVectorMap
                </p>
            </td>
            <td>
                <p>
                    Generates a vector map of channels. It draws a line of length w(x, y) and orientation &theta;(x, y) at each spatial location.
                </p>
                <p>
                    Inputs:<br/>
                    centerlines: a binary matrix that indicates centerline locations<br/>
                    orient: local orientation at each spatial location (x,y)<br/>
                    widthMap: estimated width at each spatial location (x,y)<br/>
                    saveDest: output figure save destination
                </p>
                <p>
                    Keyword Arguments:<br/>
                    thickness: thickness of the lines (default 0.2)
                </p>
                <p>
                    Returns:<br/>
                    None (saves the figure at saveDest)
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    visualization.quiverPlot
                </p>
            </td>
            <td>
                <p>
                    Generates a quiver plot that shows channel orientation and singularity index response strength.
                </p>
                <p>
                    Inputs:<br/>
                    psi: singularity index response<br/>
                    orient: local orientation at each spatial location (x,y)<br/>
                    saveDest: output figure save destination
                </p>
                <p>
                    Returns:<br/>
                    None (saves the figure at saveDest)
                </p>
            </td>
        </tr>
    </tbody>
</table>
