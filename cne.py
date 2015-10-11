# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:59:51 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/
"""

import cv2
import numpy as np
from scipy.signal import fftconvolve
from scipy.ndimage import sum as ndsum
from scipy.ndimage import label as ndlabel

class ChannelNetworkExtractor:

    def __init__(self, minScale=1.5, nrScales=15):
        """ Initialize the extractor parameters.

        Keyword arguments:
        minScale -- minimum scale sigma (default 1.5 pixels)
        nrScales -- number of scales (default 15)
        """

        self.minScale = minScale
        self.nrScales = nrScales
        self.completionFlag = 0


    def createFilters(self):
        """ Create filters.

        The filters can be used for processing many input images once the
        filters are created.
        """

        # Create the debiasing filter
        sigmad  = 5 * self.minScale
        ksized  = int(sigmad*3) #kernel half size
        self.Gdebias = cv2.getGaussianKernel(2*ksized+1, sigmad)

        # Set sigma and kernel size for the second and first order derivatives
        sigma2   = self.minScale
        sigma1   = self.minScale*1.7754
        ksize2   = int(sigma2*3) + 1
        ksize1   = int(sigma1*3) + 1

        # Set steerable filter basis orientations
        theta1 = 0
        theta2 = np.pi/3
        theta3 = 2*np.pi/3

        # Create a meshgrid for second order derivatives
        X, Y = np.meshgrid(range(-ksize2,ksize2+1), range(-ksize2,ksize2+1))
        u1 = X*np.cos(theta1) - Y*np.sin(theta1)
        u2 = X*np.cos(theta2) - Y*np.sin(theta2)
        u3 = X*np.cos(theta3) - Y*np.sin(theta3)

        # Create an isotropic Gaussian.
        # All second derivatives are defined in terms of G0
        self.G01d = cv2.getGaussianKernel(2*ksize2+1, sigma2)
        G0 = self.G01d * self.G01d.T

        # Compute second partial derivatives of Gaussian
        self.G20   = (((u1**2)/(sigma2**4)) - (1/(sigma2**2))) * G0
        self.G260  = (((u2**2)/(sigma2**4)) - (1/(sigma2**2))) * G0
        self.G2120 = (((u3**2)/(sigma2**4)) - (1/(sigma2**2))) * G0

        # Create a separable basis filter for first partial derivative of Gaussian
        x_1  = np.linspace(-ksize1, ksize1, 2*ksize1+1)
        x_1  = np.reshape(x_1, (1, -1))
        self.G0_a = cv2.getGaussianKernel(2*ksize1+1, sigma1)
        self.G1   = -((1/sigma1)**2) * x_1 * self.G0_a.T

        # Set the completion flag.
        self.completionFlag = 1
    
    def mndwi(self, green, mir, contrastStretch=True):
        """ Computes the modified normalized difference water index
        
        Input Arguments:
        green -- green band (e.g. Landsat 8 band 3)
        mir -- middle infrared band (e.g. Landsat 8 band 6)
        
        Returns:
        mndwi -- mndwi response
        """
        
        if green.dtype == 'uint8':
            green = green.astype('float')/255
         
        if mir.dtype == 'uint8':
            mir   = mir.astype('float')/255
        
        numerator = green-mir
        denominator = green+mir
        numerator[numerator<0] = 0
        numerator[denominator==0] = 0
        denominator[denominator==0] = 1
        
        mndwi = numerator / denominator
        
        if contrastStretch:
            mndwi = mndwi/np.max(mndwi)
        
        return mndwi

    def applyFilters(self, I1):
        """ Apply the filters to a given input image to compute the
        modified multiscale singularity index response. Estimate the width
        and the dominant orientation angle for each spatial location.

        Input Argument:
        I1 -- input image (e.g. Landsat NIR band or MNDWI)

        Returns:
        psi -- the singularity index response
        widthMap -- estimated width for each (x,y)
        """

        if self.completionFlag < 1:
            print "Error: You should run createFilters first to create filters"
            return None
        
        if I1.dtype == 'uint8':
            I1   = I1.astype('float')/255
            
        R, C = I1.shape

        # Compute the multiscale singularity index
        for s in range(0, self.nrScales):
            print "Processing scale: " + str(s)

            # Downscale the image to the current scale (faster than increasing the sigma)
            if s > 0:
                I1 = cv2.resize(I1, (int(C/(np.sqrt(2)**s)), int(R/(np.sqrt(2)**s))), interpolation = cv2.INTER_CUBIC)

            # Debias the image.
            mu = cv2.sepFilter2D(I1, cv2.CV_64FC1, self.Gdebias, self.Gdebias.T, borderType=cv2.BORDER_REFLECT_101)
            I = I1 - mu

            # Apply the second order derivative filters
            J20     = fftconvolve(I,self.G20,   mode='same')
            J260    = fftconvolve(I,self.G260,  mode='same')
            J2120   = fftconvolve(I,self.G2120, mode='same')

            # Compute the dominant local orientation
            Nr = np.sqrt(3) * ( (J260**2) - (J2120**2) + (J20*J260) - (J20*J2120) )
            Dr = 2*(J20**2) - (J260**2) - (J2120**2) + (J20*J260) - 2*(J260*J2120) + (J20*J2120)
            angles = np.arctan2(Nr,Dr) / 2

            # Apply the first order derivative filters
            J0u  = cv2.sepFilter2D(I, cv2.CV_64FC1, self.G1.T, self.G0_a.T, borderType=cv2.BORDER_REFLECT_101)
            J90u = cv2.sepFilter2D(I, cv2.CV_64FC1, self.G0_a, self.G1, borderType=cv2.BORDER_REFLECT_101)

            # Compute 0th, 1st, and 2nd derivatives along the estimated direction
            J0 = cv2.sepFilter2D(I, cv2.CV_64FC1, self.G01d, self.G01d.T, borderType=cv2.BORDER_REFLECT_101)
            J1 = J0u * np.cos(angles) + J90u * np.sin(angles)
            J2 =((1+(2*np.cos(2*angles)))*J20 + \
                 (1-np.cos(2*angles)+(np.sqrt(3)*np.sin(2*angles)))*J260 + \
                 (1-np.cos(2*angles)-(np.sqrt(3)*np.sin(2*angles)))*J2120) / 3

            # Compute the singularity index for the current scale
            psi_scale = np.abs(J0)*J2 / ( 1 + np.abs(J1)**2 )

            # Suppress island response (channels have negative response)
            psi_scale[psi_scale>0] = 0
            psi_scale = -psi_scale

            # Resize scale responses to the same size for element-wise comparison
            if s > 0:
                psi_scale = cv2.resize(psi_scale, (C, R), interpolation = cv2.INTER_CUBIC)
                angles = cv2.resize(angles, (C, R), interpolation = cv2.INTER_NEAREST)

            # Compute the channel width, dominant orientation, and norm of the response across scales
            if s == 0:
                psi_max = psi_scale
                psi_sum = psi_scale
                self.orient = angles
                self.widthMap = self.minScale * (np.sqrt(2)**s) * (psi_scale)
                self.psi = psi_scale**2
            else:
                idx = psi_scale > psi_max
                psi_max[idx] = psi_scale[idx]
                psi_sum = psi_sum + psi_scale
                self.orient[idx] = angles[idx]
                self.widthMap = self.widthMap + self.minScale * (np.sqrt(2)**s) * (psi_scale)
                self.psi = self.psi + psi_scale**2

        self.widthMap[psi_sum>0] = self.widthMap[psi_sum>0] / psi_sum[psi_sum>0]
        self.psi = np.sqrt(self.psi)

        # Set completion flag
        self.completionFlag = 2

        return self.psi, self.widthMap


    def extractCenterlines(self):
        """ Use non-maxima suppression to extract centerlines.
        This function uses the previously computed singularity index response (psi)
        and the dominant orientation (orient).

        Returns:
        NMS -- Non-maxima suppressed singularity index response (centerlines)
        """

        if self.completionFlag < 2:
            print "Error: You should run applyFilters first"
            return None

        # Bin orientation values
        Q = ((self.orient + np.pi/2) * 4 / np.pi + 0.5).astype('int') % 4

        # Handle borders
        mask = np.zeros(self.psi.shape, dtype='bool')
        mask[1:-1, 1:-1] = True

        # Find maxima along local orientation
        self.NMS = np.zeros(self.psi.shape)
        for q, (di, dj) in zip(range(4), ((1, 0), (1, 1), (0, 1), (-1, 1))):
            for i, j in zip(*np.nonzero(np.logical_and(Q == q, mask))):
                if self.psi[i, j] > self.psi[i + di, j + dj] and self.psi[i, j] > self.psi[i - di, j - dj]:
                    self.NMS[i, j] = self.psi[i,j]

        # Set completion flag
        self.completionFlag = 3

        return self.NMS


    def thresholdCenterlines(self, tLow=0.015, tHigh=0.025):
        """ Use a continuity-preserving hysteresis thresholding to classify
        centerlines.

        Keyword Arguments:
        tLow -- lower threshold (default 0.01)
        tHigh -- higher threshold (default 0.03)

        Returns:
        centerlines -- a binary matrix that indicates centerline locations
        """
        
        # TODO: tune parameters on a dataset
        
        if self.completionFlag < 3:
            print "Error: You should run extractCenterlines first"
            return None

        strongCenterline    = self.NMS >= tHigh
        centerlineCandidate = self.NMS >= tLow

        # Find connected components that has at least one strong centerline pixel
        strel = np.ones((3, 3), dtype=bool)
        cclabels, numcc = ndlabel(centerlineCandidate, strel)
        sumstrong = ndsum(strongCenterline, cclabels, range(1, numcc+1))
        centerlines = np.hstack((0, sumstrong > 0)).astype('bool')
        self.centerlines = centerlines[cclabels]

        # Set completion flag
        self.completionFlag = 4

        return self.centerlines


    def generateRasterMap(self, thickness=5):
        """ Generate a raster map of channels. It draws a line of length
        w(x, y) and orientation θ(x, y) at each spatial location.

        Keyword Argument:
        thickness -- thickness of the lines (default 5)

        Returns:
        raster -- the raster map
        """

        if self.completionFlag < 4:
            print "Error: You should run hysteresisThresholding first"
            return None

        centerlineWidth       = self.widthMap[self.centerlines]
        centerlineOrientation = self.orient[self.centerlines]
        centerlineStrength    = self.psi[self.centerlines]

        [row,col] = np.where(self.centerlines)

        x_off = -centerlineWidth * np.cos(centerlineOrientation)
        y_off =  centerlineWidth * np.sin(centerlineOrientation)
        lines = np.vstack((col-x_off, row-y_off, col+x_off, row+y_off)).T

        self.raster = np.zeros(self.NMS.shape)

        for i in np.argsort(centerlineStrength): #range(0, len(lines)):
            cv2.line(self.raster, (int(lines[i,0]), int(lines[i,1])), \
                                  (int(lines[i,2]), int(lines[i,3])), \
                                  centerlineStrength[i], thickness)

        return self.raster


    def exportShapeFile():
        # TODO: implement
        return None