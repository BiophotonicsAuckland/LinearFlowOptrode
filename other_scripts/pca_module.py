import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import scale
import os, random

def colors(n):
    ret = []
    r = int(random.random() * 256)
    g = int(random.random() * 256)
    b = int(random.random() * 256)
    step = 256 / n
    for i in range(n):
        r += step
        g += step
        b += step
        r =( int(r) % 256)
        g = (int(g) % 256)
        b = (int(b) % 256)
        ret.append((r/256,g/256,b/256)) 
    return ret

class PCASpectra:
    """This class takes spectra data containing a 2D matrix of intensitiesn and allows PCA analysis and plotting"""

    def __init__(self, spectra):
        self.no_measure= 5 # measurements per sample  this value needs to be accurate for the scatter plot to work
     
        spectra = scale(spectra,with_std=False,axis=1,with_mean=True)
     
        print("X_SHAPE:",spectra.shape)
        pca = PCA(n_components=5)#spectra.shape[1])
        pca.fit(spectra)
        
        var= pca.explained_variance_ratio_
        var1=np.cumsum(np.round(pca.explained_variance_ratio_, decimals=4)*100)
        plt.clf()
        plt.title("Variance")
        plt.xlabel("# of PC ")
        plt.ylabel("Explained variance")
        plt.plot(var1)
        plt.savefig("ExplainedVar.png",format="png")
        self.X1=pca.transform(spectra)#X1 is the dimensionally reduced datase
        
        self.loadings = pca.components_#The loadings is the PCA vector components, Kx1 vector, with n component vectors
        print(len(self.loadings))
        np.savetxt("loadings.csv",self.loadings.T,delimiter=",")
        np.savetxt("scores.csv",self.X1,delimiter=",")
    
    
    def lineLoadingPlot(self,title):
        plt.clf()
        plt.plot(self.loadings[0])
        plt.title("PC1 Loading Plot "+title)
        plt.xlabel("features")
        plt.ylabel("PC1")
        plt.savefig(title+"loading.png",format="png")
        
    def scatterScorePlot(self, title):
        plt.clf()
        print("Score Shape: ",self.X1.shape)
        
        n_colors_len  = self.X1.shape[1]//self.no_measure +1
        color_vec  = colors(n_colors_len)
        
        for i in range(self.X1.shape[1]): #iterate over the samples
            c_index = i//self.no_measure #int division
            plt.scatter(self.X1[0,i],self.X1[1,i],c=color_vec[c_index])#Scatter plot of PC1 and PC2
        plt.title("Score")
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        plt.savefig(title+" Scatter.png",format="png")   
    
   
    #scatterScorePlot(X1,"PC1 vs PC2 Scatter")
    #slineLoadingPlot(loadings[0],"Loading of PC1")
    