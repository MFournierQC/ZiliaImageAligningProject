import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def display (firstEye, secondEye, firstSO2Matrix, secondSO2Matrix):
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].imshow(firstEye)
    axs[0, 0].set_title('first eye')
    axs[0, 0].axis('off')
    axs[0, 1].imshow(secondEye)
    axs[0, 1].set_title('second eye')
    axs[0, 1].axis('off')

    minValue,maxValue=colorMapRange(firstSO2Matrix,secondSO2Matrix)

    axs[1, 0].imshow(firstSO2Matrix,cmap=plt.cm.coolwarm, vmin =minValue, vmax = maxValue)
    axs[1, 0].set_title('saturated oxygen (1st eye)')
    axs[1, 0].axis('off')
    cmp = axs[1, 1].imshow(secondSO2Matrix,cmap=plt.cm.coolwarm, vmin =minValue, vmax = maxValue)
    axs[1, 1].set_title('saturated oxygen (2nd eye)')
    axs[1, 1].axis('off')
    fig.colorbar(cmp , ax=axs[1, :], location='bottom',shrink=0.6)
    plt.show()
    return None

def colorMapRange (firstImage,secondImage):
    minValue=np.min(np.array([np.min(firstImage),np.min(secondImage)]))
    maxValue = np.max(np.array([np.max(firstImage), np.max(secondImage)]))
    return minValue,maxValue

def matrixSO2(labels,saturationValues,leftEye=False):
    yLabel = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'J', 'K', 'L', 'M'])
    if leftEye==False :
        xLabel = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])

    if leftEye==True :
        xLabel = np.array(['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'])

        
    concentrationMatrix = np.zeros([10, 10])

    for i in range(saturationValues.shape[0]):
        splitLabel = np.array(list(labels[i]))


        concentrationMatrix[int(np.where(np.array(splitLabel[0]) == xLabel)[0]),
                            int(np.where(np.array(splitLabel[1]) == yLabel)[0])] =saturationValues[i]
    
    return concentrationMatrix


def testPlot():
    eye1=np.random.rand(1000,1000)
    eye2 = np.random.rand(1000, 1000)
    SO1 = np.random.rand(10, 10)
    SO2 = np.random.rand(10, 10)
    display(eye1,eye2,SO1,SO2)
    return None

# xLabel = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
# a= np.array(['4B'])
# k=np.array(list(a[0]))
# print(list(a[0]))
#
# print(  (np.where(k[0] == xLabel)[0]) )
###################

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

from skimage.io import imread
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from skimage import color
import scipy

img=imread('/Users/elahe/Documents/Bresil 1511184-20210525T145240Z-001/Bresil 1511184/20210316-095955-bresil-od-onh-rlp2/001-eye.jpg')
# img=imread('/Users/elahe/Documents/Bresil 1511184-20210525T145240Z-001/Bresil 1511184/20210316-100153-bresil-od-onh-rlp6/001-eye.jpg')

img[:,:,2]=0

imgGray = color.rgb2gray(img)**1.5
# imgGray=img[:,:,0]
# imgGray=(imgGray-np.min(imgGray))/(np.max(imgGray)-np.min(imgGray))

Threshold = 0.4
w=10
L=np.mean(imgGray,axis=0)
L=(L-np.min(L))/(np.max(L)-np.min(L))
L=np.round(L,2)
dL = np.gradient(L)



# print(np.min(np.where(dL > 0.0051)))
# print(np.max(np.where(dL > 0.0051)))
H=np.mean(imgGray,axis=1)
H=(H-np.min(H))/(np.max(H)-np.min(H))

H=np.round(H,2)
dH = np.gradient(H)
# print(np.min(np.where(dH > 0.005)))
# print(np.max(np.where(dH > 0.005)))

plt.imshow(imgGray)
plt.show()

plt.plot(L)


plt.show()

plt.plot(np.abs(dL))
plt.show()

plt.plot(H)
plt.show()

plt.plot(np.abs(dH))
plt.show()