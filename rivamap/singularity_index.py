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

class SingularityIndexFilters:
    
    def __init__(self, minScale=1.2, nrScales=15):
        """ Initializes the parameters and filters
    
        Keyword arguments:
        minScale -- minimum scale sigma (default 1.2 pixels)
        nrScales -- number of scales (default 15)
        """
    
        self.minScale = minScale
        self.nrScales = nrScales
        self._createFilters()
        
        
    def _createFilters(self):
        """ Creates the filters that are needed for computing the modified
        multiscale singularity index response. The filters can be used for
        processing many input images once the filters are created.
        """
    
        # Create the debiasing filter
        sigmad  = 5 * self.minScale
        ksized  = int(sigmad*3) #kernel half size
        self.Gdebias = cv2.getGaussianKernel(2*ksized+1, sigmad)
    
        # Set sigma and kernel size for the second and first order derivatives
        sigma2   = float(self.minScale)
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
        
        # Set the completion flag
        self.isCreated = True
        

def applyMMSI(I1, filters, togglePolarity=False):
    """ Applies the filters to a given input image to compute the
    modified multiscale singularity index response. Estimate the width
    and the dominant orientation angle for each spatial location.

    Inputs:
    I1 -- input image (e.g. Landsat NIR band or MNDWI)
    filters -- an instance of SingularityIndexFilters class that contains
               precomputed filters

    Keyword arguments:
    togglePolarity -- changes polarity, use if the rivers are darker
                      than land in the input image (i.e. SAR images)

    Returns:
    psi -- the singularity index response
    widthMap -- estimated width at each spatial location (x,y)
    orient -- local orientation at each spatial location (x,y)
    """
        
    if I1.dtype == 'uint8':
        I1   = I1.astype('float')/255
        
    if I1.dtype == 'uint16':
        I1   = I1.astype('float')/65535
        
    if len(I1.shape) > 2:
        raise ValueError('This function inputs only a singe channel image')
        
    R, C = I1.shape
    
    # Compute the multiscale singularity index
    for s in range(0, filters.nrScales):
        print "Processing scale: " + str(s)

        # Downscale the image to the current scale (faster than increasing the sigma)
        if s > 0:
            I1 = cv2.resize(I1, (int(C/(np.sqrt(2)**s)), int(R/(np.sqrt(2)**s))), \
                            interpolation = cv2.INTER_CUBIC)

        # Debias the image.
        mu = cv2.sepFilter2D(I1, cv2.CV_64FC1, filters.Gdebias, filters.Gdebias.T, \
                                borderType=cv2.BORDER_REFLECT_101)
        I = I1 - mu

        # Apply the second order derivative filters
        J20     = fftconvolve(I, filters.G20,   mode='same')
        J260    = fftconvolve(I, filters.G260,  mode='same')
        J2120   = fftconvolve(I, filters.G2120, mode='same')

        # Compute the dominant local orientation
        Nr = np.sqrt(3) * ( (J260**2) - (J2120**2) + (J20*J260) - (J20*J2120) )
        Dr = 2*(J20**2) - (J260**2) - (J2120**2) + (J20*J260) - 2*(J260*J2120) + (J20*J2120)
        angles = np.arctan2(Nr,Dr) / 2

        # Apply the first order derivative filters
        J0u  = cv2.sepFilter2D(I, cv2.CV_64FC1, filters.G1.T, filters.G0_a.T, \
                                borderType=cv2.BORDER_REFLECT_101)
        J90u = cv2.sepFilter2D(I, cv2.CV_64FC1, filters.G0_a, filters.G1, \
                                borderType=cv2.BORDER_REFLECT_101)

        # Compute 0th, 1st, and 2nd derivatives along the estimated direction
        J0 = cv2.sepFilter2D(I, cv2.CV_64FC1, filters.G01d, filters.G01d.T, \
                                borderType=cv2.BORDER_REFLECT_101)
        J1 = J0u * np.cos(angles) + J90u * np.sin(angles)
        J2 =((1+(2*np.cos(2*angles)))*J20 + \
             (1-np.cos(2*angles)+(np.sqrt(3)*np.sin(2*angles)))*J260 + \
             (1-np.cos(2*angles)-(np.sqrt(3)*np.sin(2*angles)))*J2120) / 3

        # Compute the singularity index for the current scale
        psi_scale = np.abs(J0)*J2 / ( 1 + np.abs(J1)**2 )

        # Resize scale responses to the same size for element-wise comparison
        if s > 0:
            psi_scale = cv2.resize(psi_scale, (C, R), interpolation = cv2.INTER_CUBIC)
            angles = cv2.resize(angles, (C, R), interpolation = cv2.INTER_NEAREST)

        # Toggle polarity if needed
        if togglePolarity:
            psi_scale = -psi_scale

        # Suppress island response (channels have negative response unless the polarity is changed)
        psi_scale[psi_scale>0] = 0
        psi_scale = np.abs(psi_scale)

        # Gamma normalize response
        psi_scale = psi_scale * filters.minScale**2
                
        # Find the dominant scale, orientation, and norm of the response across scales
        if s == 0:
            # response buffer (we need the neighbors of the dominant scale for width estimation)
            psi_prev = np.zeros(psi_scale.shape)
            psi_curr = np.zeros(psi_scale.shape)
            psi_next = psi_scale
            
            # response at the dominant scale and its neighbors
            psi_max_curr = np.zeros(psi_scale.shape)
            psi_max_prev = np.zeros(psi_scale.shape)
            psi_max_next = np.zeros(psi_scale.shape)
            
            dominant_scale_idx = np.zeros(psi_scale.shape)
            orient = angles
            psi_max = psi_scale
            psi = psi_scale**2
                        
        else:
            psi_prev = psi_curr
            psi_curr = psi_next
            psi_next = psi_scale
            
            idx_curr = psi_curr > psi_max_curr
            psi_max_curr[idx_curr] = psi_curr[idx_curr]
            psi_max_prev[idx_curr] = psi_prev[idx_curr]
            psi_max_next[idx_curr] = psi_next[idx_curr]
            
            idx = psi_scale > psi_max            
            psi_max[idx] = psi_scale[idx]
            dominant_scale_idx[idx] = s
            orient[idx] = angles[idx]
            psi = psi + psi_scale**2
            
    # Check if the coarsest scale has the maximum response
    psi_prev = psi_curr
    psi_curr = psi_next
    idx_curr = psi_curr > psi_max_curr
    psi_max_curr[idx_curr] = psi_curr[idx_curr]
    psi_max_prev[idx_curr] = psi_prev[idx_curr]
    psi_max_next[idx_curr] = 0    
    
    # Euclidean norm of the response across scales
    psi = np.sqrt(psi)
    
    # Estimate the width by fitting a quadratic spline to the response at the 
    # dominant scale and its neighbors
    s_prev = filters.minScale * (np.sqrt(2)**(dominant_scale_idx-1))
    s_max = filters.minScale * (np.sqrt(2)**(dominant_scale_idx))
    s_next = filters.minScale * (np.sqrt(2)**(dominant_scale_idx+1))

    A = s_next * (psi_max - psi_max_prev) + \
        s_max * (psi_max_prev - psi_max_next) + \
        s_prev * (psi_max_next - psi_max)
    B = s_next*s_next * (psi_max_prev - psi_max) + \
        s_max*s_max * (psi_max_next - psi_max_prev) + \
        s_prev*s_prev * (psi_max - psi_max_next)
    widthMap = np.zeros(psi.shape)
    widthMap[psi>0] = -B[psi>0] / (2*A[psi>0])

    # Scaling factor for narrow rivers
    scalingFactor = 2/(1+np.exp(-8*psi))-1
    widthMap = scalingFactor * widthMap + 0.5

    return psi, widthMap, orient
