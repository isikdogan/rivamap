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
        

    def applyFilters(self, I1):
        
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
            psi_scale[psi_scale>0] = 0;
            psi_scale = -psi_scale
                
            # Resize scale responses to the same size for element-wise comparison
            if s > 0:
                psi_scale = cv2.resize(psi_scale, (R, C), interpolation = cv2.INTER_CUBIC)
                angles = cv2.resize(angles, (R, C), interpolation = cv2.INTER_NEAREST)
        
            filename = "psi_scale_" + str(s) + ".png"
            cv2.imwrite(filename, cv2.normalize(psi_scale, None, 0, 255, cv2.NORM_MINMAX))
            
            # Compute the maximum response across scales
            if s == 0:
                psi = psi_scale
                orient = angles
                scaleMap = np.zeros((R,C))
            else:
                idx = psi_scale > psi
                psi[idx] = psi_scale[idx]
                scaleMap[idx] = s
                orient[idx] = angles[idx]
                
                
        return psi, orient