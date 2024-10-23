import create_presistent_diagram as cp
import get_topological_subnet_pd as tp
import numpy as np
from gtda.homology import VietorisRipsPersistence
from gtda.plotting import plot_diagram
import os
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from gtda.diagrams import PersistenceEntropy
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
from persim import PersistenceImager
from ripser import Rips

# Extract Persistence Entropy Features
def extract_entropy_features(diagrams):
  PE = PersistenceEntropy()
  features = PE.fit_transform(diagrams)
  return features

# Get Persistence Images
def get_max_birth_persistence(all_diagrams):

    max_birth = 0
    max_persistence = 0

    min_birth = np.inf
    min_persistence = np.inf

    for diagrams in all_diagrams:
        
        for diagram in diagrams[1:]: 
            if len(diagram) > 0:  
                births = diagram[:, 0]
                persistences = diagram[:, 1] - diagram[:, 0]  
                max_birth = max(max_birth, np.max(births))
                max_persistence = max(max_persistence, np.max(persistences))

                min_birth = min(min_birth, np.min(births))
                min_persistence = min(min_persistence, np.min(persistences))
    
    return max_birth, min_birth, max_persistence, min_persistence

def create_persistent_images(diagrams, pimgr, save_path="persistent_image.png", savefig=True):

    H0_dgm, H1_dgm, H2_dgm = diagrams
     
    # Transform diagrams into persistent images using the already fitted PersistenceImager
    
    H1_img = pimgr.transform(H1_dgm, skew=True)
    H2_img = pimgr.transform(H2_dgm, skew=True)

    # If True, save the persistence image
    if savefig == True:
        
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))

        # Plot H1 Persistent Image
        pimgr.plot_image(H1_img, ax=axs[0])
        axs[0].set_title("H1 Persistent Image")
        axs[0].axis('on')
        
        # Plot H2 Persistent Image
        pimgr.plot_image(H2_img, ax=axs[1])
        axs[1].set_title("H2 Persistent Image")
        axs[1].axis('on')

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"Saved persistent images to {save_path}")
    
    
    img_list=[H1_img, H2_img]

    #Flatten image array
    img_array = np.vstack(img_list).ravel()

    return img_array

def plot_birth_presistence_diagrams(diagrams, max_birth=50, max_persistence=50, save_path="persistent_image.png"):

    H0_dgm, H1_dgm, H2_dgm = diagrams

    rips = Rips()
  
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))  
    
    # Plot the persistence diagram for H0
    rips.plot(H0_dgm, ax=axs[0], show=False, lifetime=True)
    axs[0].set_title("H0 Persistence Diagram (Persistence vs Birth)")
    axs[0].set_xlabel("Birth")
    axs[0].set_ylabel("Persistence")
    
    # Plot the persistence diagram for H1
    rips.plot(H1_dgm, ax=axs[1], show=False, lifetime=True, xy_range=[0, max_birth, 0, max_persistence])
    axs[1].set_title("H1 Persistence Diagram (Persistence vs Birth)")
    axs[1].set_xlabel("Birth")
    axs[1].set_ylabel("Persistence")
    
    # Plot the persistence diagram for H2
    rips.plot(H2_dgm, ax=axs[2], show=False, lifetime=True, xy_range=[0, max_birth, 0, max_persistence])
    axs[2].set_title("H2 Persistence Diagram (Persistence vs Birth)")
    axs[2].set_xlabel("Birth")
    axs[2].set_ylabel("Persistence")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return print(f"Saved persistent diagrams to {save_path}")

def get_persistent_features(diagrams, filenames, export_folder, maxdim=2, coeff=2, pixel_size=0.2, savefig=True):
        
    # Get min, max birth and min, max persistence for the dataset
    # This makes sure that the persistence images are plotted on the same scale for the entire dataset
    max_birth, min_birth, max_persistence, min_persistence= get_max_birth_persistence(diagrams)
    print(f"Max birth: {max_birth}, Min birth: {min_birth}, Max persistence: {max_persistence}, Min persistence: {min_persistence}")
    
    pimgr = PersistenceImager(
        pixel_size=pixel_size,
        birth_range=(min_birth, max_birth),  
        pers_range=(min_persistence, max_persistence))
    image_features=[]

    for idx, diagrams in enumerate(diagrams):

        save_path = f"{export_folder}/{filenames[idx]}_persistent_image_array.png"
        features=create_persistent_images(diagrams, pimgr, save_path=save_path, savefig=savefig)
        image_features.append(features)

        save_path_diagrams = f"{export_folder}/{filenames[idx]}_persistent_diagram.png"
        plot_birth_presistence_diagrams(diagrams, max_birth=max_birth, max_persistence=max_persistence, save_path=save_path_diagrams)

    return image_features

