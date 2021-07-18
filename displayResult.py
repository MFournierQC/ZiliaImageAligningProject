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

    axs[1, 0].imshow(firstSO2Matrix,cmap=plt.cm.YlGn, vmin =minValue, vmax = maxValue)
    axs[1, 0].set_title('saturated oxygen (1st eye)')
    axs[1, 0].axis('off')
    cmp = axs[1, 1].imshow(secondSO2Matrix,cmap=plt.cm.YlGn, vmin =minValue, vmax = maxValue)
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
    if leftEye==False :
        xLabel = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        yLabel = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'J', 'K', 'L', 'M'])
    if leftEye==True :
        xLabel = np.array(['10', '9', '8', '7', '6', '5', '4', '3', '2', '1'])
        yLabel = np.array(['M', 'L', 'K', 'J', 'F', 'E', 'D', 'C', 'B', 'A'])
        
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