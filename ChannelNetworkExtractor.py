# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:59:51 2015

@author: leo
"""

import numpy as np
import cv2
from scipy.signal import fftconvolve

class ChannelNetworkExtractor:
    
    def __init__(self, minScale=1.5, nrScales=15):
        self.minScale = minScale        
        self.nrScales = nrScales
        self.completionFlag = 0
        
    def createFilters(self):

        # Debiasing filter
        sigmad  = 5 * self.minScale
        ksized  = int(sigmad*3) #kernel half size
        self.Gdebias = cv2.getGaussianKernel(2*ksized+1, sigmad)
        
        # Set sigma and kernel size for the second and first order derivatives
        sigma2   = self.minScale
        sigma1   = self.minScale*1.7754
        ksize2   = int(sigma2*3) + 1
        ksize1   = int(sigma1*3) + 1
        
        # Steerable filter basis orientations
        theta1 = 0
        theta2 = np.pi/3
        theta3 = 2*np.pi/3
        
        # Create a meshgrid for second order derivatives
        X, Y = np.meshgrid(range(-ksize2,ksize2+1), range(-ksize2,ksize2+1))
        u1 = X*np.cos(theta1) - Y*np.sin(theta1)
        u2 = X*np.cos(theta2) - Y*np.sin(theta2)
        u3 = X*np.cos(theta3) - Y*np.sin(theta3)
        
        # All second derivatives are defined in terms of G0
        self.G01d = cv2.getGaussianKernel(2*ksize2+1, sigma2)
        G0 = self.G01d * self.G01d.T
        
        # Second partial derivatives of gaussian
        self.G20   = (((u1**2)/(sigma2**4)) - (1/(sigma2**2))) * G0
        self.G260  = (((u2**2)/(sigma2**4)) - (1/(sigma2**2))) * G0
        self.G2120 = (((u3**2)/(sigma2**4)) - (1/(sigma2**2))) * G0
        
        # Separable basis filter for first partial derivative of gaussian
        x_1  = np.linspace(-ksize1, ksize1, 2*ksize1+1)
        x_1  = np.reshape(x_1, (1, -1))
        self.G0_a = cv2.getGaussianKernel(2*ksize1+1, sigma1)
        self.G1   = -((1/sigma1)**2) * x_1 * self.G0_a.T
        
        # Set completion flag
        self.completionFlag = 1

    def applyFilters(self, I1):
        
        if self.completionFlag < 1:
            print "Error: You should run createFilters first to create filters"
            return None
        
        I1 = cv2.normalize(I1.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)
        R, C = I1.shape
        
        # Compute the multiscale singularity index
        for s in range(0, self.nrScales):
        
            print "Processing scale: " + str(s)    
            
            # Downscale the image to the current scale (faster than increasing the sigma)
            if s > 0:
                I1 = cv2.resize(I1, (int(R/(np.sqrt(2)**s)), int(C/(np.sqrt(2)**s))), interpolation = cv2.INTER_CUBIC)
        
            # Debias the image
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
            J90u  = cv2.sepFilter2D(I, cv2.CV_64FC1, self.G0_a, self.G1, borderType=cv2.BORDER_REFLECT_101)
            
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
                psi_scale = cv2.resize(psi_scale, (R, C), interpolation = cv2.INTER_CUBIC)
                angles = cv2.resize(angles, (R, C), interpolation = cv2.INTER_NEAREST)
                    
            # Compute the maximum response across scales
            if s == 0:
                self.psi = psi_scale
                self.orient = angles
                self.scaleMap = np.zeros((R,C))
                self.energy = psi_scale**2
            else:
                idx = psi_scale > self.psi
                self.psi[idx] = psi_scale[idx]
                self.scaleMap[idx] = s
                self.orient[idx] = angles[idx]
                self.energy = self.energy + psi_scale**2
        
        # Set completion flag
        self.completionFlag = 2
        
        # TODO: interpolate between scales to estimate the width
        
        return self.psi, self.scaleMap
            
    
    def extractCenterlines(self):
        
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
        
    def generateRasterMap(self):
        
        # TODO: clean up
        
        if self.completionFlag < 3:
            print "Error: You should run extractCenterlines first"
            return None
        
        # TODO: implement a centerline classifier instead of hard thresholding
        centerlines = self.NMS > 0.03
            
        centerlineWidth       = self.minScale * np.sqrt(2)**self.scaleMap[centerlines]
        centerlineOrientation = self.orient[centerlines]
        
        [row,col] = np.where(centerlines)
        
        x_off = -centerlineWidth * np.cos(centerlineOrientation)
        y_off = centerlineWidth * np.sin(centerlineOrientation)
        lines = np.vstack((col-x_off, row-y_off, col+x_off, row+y_off)).T
        
        self.raster = np.zeros(self.NMS.shape)
        
        for i in range(0, len(lines)):
            cv2.line(self.raster, (int(lines[i,0]), int(lines[i,1])), (int(lines[i,2]), int(lines[i,3])), 255)

        return None
        
    def exportShapeFile():
        # TODO: implement
        return None
        
        
        
        
        