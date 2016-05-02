## Channel Network Extractor

#### Related papers

* Isikdogan, F., A.C. Bovik, and P. Passalacqua (2016). LarMap: A Framework for Creating Large-scale River Maps using Satellite Imagery, unpublished.
* Isikdogan, F., A.C. Bovik, and P. Passalacqua (2015). Automatic Channel Network Extraction From Remotely Sensed Images by Singularity Analysis, *IEEE Geoscience and Remote Sensing Letters*, 12, 11, 2218-2221. [[**Read at IEEExplore**]](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=7192616), [[**PDF**]](http://live.ece.utexas.edu/publications/2015/Isikdogan_GRSL_2015_Channel_Network_Extraction.pdf)

#### Example Use
For an example use of the framework please see [example.ipynb](./examples/example.ipynb)

#### Example Results

<a href="http://live.ece.utexas.edu/research/cne/img/keithsburg.png"><img src="http://live.ece.utexas.edu/research/cne/img/keithsburg.png" alt="Example Result" height="250"></a>
<a href="http://live.ece.utexas.edu/research/cne/img/waxlake.png"><img src="http://live.ece.utexas.edu/research/cne/img/waxlake.png" alt="Example Result" height="250"></a>
<a href="http://live.ece.utexas.edu/research/cne/img/mississippi.png"><img src="http://live.ece.utexas.edu/research/cne/img/mississippi.png" alt="Example Result" height="250"></a>
<a href="http://live.ece.utexas.edu/research/cne/img/channelmapoverlaid.png"><img src="http://live.ece.utexas.edu/research/cne/img/ganges.png" alt="Example Result" height="250"></a>

#### Reference

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
                    <br/>
                     Inputs:
                    <br/>
                     green: green band (e.g. Landsat 8 band 3)
                    <br/>
                     mir: middle infrared band (e.g. Landsat 8 band 6)
                </p>
                <p>
                    <br/>
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
                    Keyword arguments:
                </p>
                <p>
                    minScale: minimum scale sigma (default 1.2 pixels)
                </p>
                <p>
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
                    Inputs:
                </p>
                <p>
                    I1: input image (e.g. Landsat NIR band or MNDWI)
                </p>
                <p>
                    filters: an instance of SingularityIndexFilters class that contains precomputed filters
                </p>
                <p>
                    togglePolarity: changes polarity, use if the rivers are darker than land in the input image (i.e. SAR images)
                </p>
                <p>
                    Returns:
                </p>
                <p>
                    psi: the singularity index response
                </p>
                <p>
                    widthMap: estimated width at each spatial location (x,y)
                </p>
                <p>
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
                    Inputs: (can be obtained by running applyMMSI function)
                </p>
                <p>
                    psi: the singularity index response
                </p>
                <p>
                    orient: local orientation at each spatial location (x,y)
                </p>
                <p>
                    Returns:
                </p>
                <p>
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
                    Uses a continuity-preserving hysteresis thresholding to classify
                </p>
                <p>
                    centerlines.
                </p>
                <p>
                    Inputs:
                </p>
                <p>
                    nms: Non-maxima suppressed singularity index response
                </p>
                <p>
                    Keyword Arguments:
                </p>
                <p>
                    bimodal: true if the areas of rivers in the image are sufficiently large that the distribution of &psi; is bimodal
                </p>
                <p>
                    tLow: lower threshold (automatically set if bimodal=True)
                </p>
                <p>
                    tHigh: higher threshold (automatically set if bimodal=True)
                </p>
                <p>
                    Returns:
                </p>
                <p>
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
                    Reads metadata from a geotiff file.
                </p>
                <p>
                    Inputs:
                </p>
                <p>
                    filepath: path to the file
                </p>
                <p>
                    Returns:
                </p>
                <p>
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
                    Saves a raster image as a geotiff file
                </p>
                <p>
                    Inputs:
                </p>
                <p>
                    gm: georeferencing metadata I: raster image filepath: path to the file
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
                    Inputs:
                </p>
                <p>
                    gm: georeferencing metadata
                </p>
                <p>
                    x, y: pixel coordinates
                </p>
                <p>
                    Returns:
                </p>
                <p>
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
                    Inputs:
                </p>
                <p>
                    gm: georeferencing metadata
                </p>
                <p>
                    lon, lat: longitude and latitude
                </p>
                <p>
                    Returns:
                </p>
                <p>
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
                    Inputs:
                </p>
                <p>
                    centerlines: a binary matrix that indicates centerline locations
                </p>
                <p>
                    widthMap: estimated width at each spatial location (x,y)
                </p>
                <p>
                    gm: georeferencing metadata filepath: path to the file
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
                    Inputs:
                </p>
                <p>
                    centerlines: a binary matrix that indicates centerline locations
                </p>
                <p>
                    orient: local orientation at each spatial location (x,y)
                </p>
                <p>
                    widthMap: estimated width at each spatial location (x,y)
                </p>
                <p>
                    Keyword Arguments:
                </p>
                <p>
                    thickness: thickness of the lines (default 3)
                </p>
                <p>
                    Returns:
                </p>
                <p>
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
                    Inputs:
                </p>
                <p>
                    centerlines: a binary matrix that indicates centerline locations
                </p>
                <p>
                    orient: local orientation at each spatial location (x,y)
                </p>
                <p>
                    widthMap: estimated width at each spatial location (x,y)
                </p>
                <p>
                    saveDest: output figure save destination
                </p>
                <p>
                    Keyword Arguments:
                </p>
                <p>
                    thickness: thickness of the lines (default 0.2)
                </p>
                <p>
                    Returns:
                </p>
                <p>
                    None (saves the figure at saveDest)
                </p>
            </td>
        </tr>
        <tr>
            <td>
                <p>
                    Visualization.quiverPlot
                </p>
            </td>
            <td>
                <p>
                    Generates a quiver plot that shows channel orientation and singularity index response strength.
                </p>
                <p>
                    Inputs:
                </p>
                <p>
                    psi: singularity index response
                </p>
                <p>
                    orient: local orientation at each spatial location (x,y)
                </p>
                <p>
                    saveDest: output figure save destination
                </p>
                <p>
                    Returns:
                </p>
                <p>
                    None (saves the figure at saveDest)
                </p>
            </td>
        </tr>
    </tbody>
</table>

</hr>