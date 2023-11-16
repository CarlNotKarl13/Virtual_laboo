import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage.measure import regionprops, label
import pandas as pd 

# INPUT DATA
Input_Image = cv2.imread('C:\\Users\\carl1\\OneDrive\\Bureau\\CESI\\v0.5\\v0.3\\testfeature1\\Big_Red_Board_6-12_Paint_Corrected.png',cv2.IMREAD_GRAYSCALE)
board_height = 800
n_bins = 10
Max_Grain_Size = 20
X, Y = Input_Image.shape
I = Input_Image > 0

# VARIABLES
binning = np.linspace(0, 1.1 * Max_Grain_Size, n_bins)
V_eq_bin = np.zeros(n_bins)
N_bin = np.zeros(n_bins)

# CALCULATIONS
pixel_size = X / board_height
Bin_Image = I.astype(np.uint8)
label_image = label(Bin_Image)  # Label connected components

# Use 'intensity_image' to specify properties
Properties_table = regionprops(label_image, intensity_image=Bin_Image)

Nb_of_Particles = len(Properties_table)
Stat_Summary = np.zeros((Nb_of_Particles, 3))

for i, prop in enumerate(Properties_table):
    major_axis_length = prop.major_axis_length
    minor_axis_length = prop.minor_axis_length
    equivalent_diameter = np.sqrt(4 * prop.area / np.pi)  # Calculate equivalent diameter using area
    Stat_Summary[i, 1] = equivalent_diameter * pixel_size
    Stat_Summary[i, 2] = 4/3 * np.pi * (equivalent_diameter / 2)**3 * pixel_size**3

D_eq = Stat_Summary[:, 1]
V_eq = Stat_Summary[:, 2]

for i in range(Nb_of_Particles):
    for j in range(1, n_bins-1):
        if binning[j-1] < D_eq[i] < binning[j]:
            V_eq_bin[j] += V_eq[i]
            N_bin[j] += 1

# OUTPUT DATA
fig_1 = plt.figure(1)
plt.plot(binning, 100 * np.cumsum(V_eq_bin)/max(np.cumsum(V_eq_bin)), 'k', linewidth=2)
plt.ylabel('Cumulative Size Distribution [%]')
plt.axis([0, max(binning), 0, 110])
plt.twinx()
plt.plot(binning, V_eq_bin/max(np.cumsum(V_eq_bin)), 'r', linewidth=2)
plt.grid()
plt.minorticks_on()
plt.xlabel('Diameter [mm]')
plt.ylabel('PSD')
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
fig_2 = plt.figure(2)
plt.imshow(I, cmap='gray')
plt.show()
# Créez une série pandas à partir des valeurs que vous souhaitez enregistrer
data = pd.Series(100 * np.cumsum(V_eq_bin)/max(np.cumsum(V_eq_bin)))

# Créez une série pandas pour binning
binning_series = pd.Series(binning)

# Créez une série pandas pour V_eq_bin/max(np.cumsum(V_eq_bin))
v_eq_ratio_series = pd.Series(V_eq_bin / max(np.cumsum(V_eq_bin)))

# Créez un DataFrame pandas à partir de toutes les séries
df = pd.DataFrame({
    'Binning (mm)': binning_series,
    'Cumulative Size Distribution (%)': data,
    'V_eq_bin_ratio': v_eq_ratio_series
})

# Enregistrez le DataFrame dans un fichier Excel
df.to_excel('v_eq_data.xlsx', index=False)  # Modifiez le nom du fichier si nécessaire