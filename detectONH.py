from zilia import *
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure
from skimage import img_as_float
from skimage.transform import resize
from scipy.ndimage.filters import generic_filter
from skimage.morphology import closing,disk,erosion
from scipy.ndimage.morphology import binary_fill_holes
from skimage.measure import label, regionprops
import pickle
from sklearn.metrics import mean_squared_error
import cv2

db = ZiliaDB()


def ExternalStatement():
    statement = "select f.path as pathImage , f.eye as eye, c.path as path, c.property, c.value from imagefiles as f left join calculations as c on c.path = f.path where c.algorithm='manual'"
    db.execute(statement)
    rows = db.fetchAll()
    images = db.getImagesFromRows(rows)
    properties = []
    for row in rows:
        properties.append(row['value'])
    return images.values(),properties



def getONHProp (img):
    img[:, :, 2] = 0
    img = rgb2gray(img)
    img = img_as_float(np.squeeze(img))
    gammaCorrected = exposure.adjust_gamma(img, 1.3)

    imageResized = resize(gammaCorrected, (img.shape[0] // 5, img.shape[1] // 5),
                           anti_aliasing=True)

    imageFiltered = generic_filter(imageResized, np.std, size=5)
    imageNormalized = ((imageFiltered-np.min(imageFiltered))/
                      (np.max(imageFiltered)-np.min(imageFiltered)))

    imageThresholded = np.zeros(imageNormalized.shape)
    imageThresholded[imageNormalized>0.2]=1

    closingDisk=disk(5)
    imageClosed=closing(imageThresholded,closingDisk)
    imageFilled = binary_fill_holes(imageClosed)
    label_img = label(imageFilled)
    regions = regionprops(label_img)
    center_coordinates = ([],[])
    axesLength = ([],[])
    for elipse in regions:
        if elipse.minor_axis_length > 60 and elipse.minor_axis_length < 100 :
            if elipse.major_axis_length > 70 and elipse.major_axis_length < 110 :
                center_coordinates = (int(elipse.centroid[1]),int(elipse.centroid[0]))
                axesLength = (int(elipse.minor_axis_length/2), int(elipse.major_axis_length/2))
    ###### This part can be used to plot the ellipse
    # if axesLength != ([],[]):
    #     angle = 0
    #     startAngle = 0
    #     endAngle = 360
    #     # Red color in BGR
    #     color = (0, 0, 255)
    #     # Line thickness of 5 px
    #     thickness = 2
    #     # Using cv2.ellipse() method
    #     # Draw a ellipse with red line borders of thickness of 5 px
    #     image = cv2.ellipse(imageResized, center_coordinates, axesLength
    #                         ,angle, startAngle, endAngle, color, thickness)
    # # Displaying the image
    #     plt.figure()
    #     plt.imshow(image)
    #     plt.show()
    return (center_coordinates , axesLength )



def plotReg(real,pred):
    real=[int(float(x)) for x in real]

    x = np.asarray(real)
    y = np.asarray(pred)
    m, b = np.polyfit(x, y, 1)

    plt.figure()
    plt.plot(x, y, 'o', label="real vs Predicted")
    plt.xlabel('manual')
    plt.ylabel('algorithm')
    plt.plot(x, m*x + b , label="regression line")
    plt.legend()

    plt.show()
    print('regression slope' , m)
    print('RMSE :', (np.sqrt(mean_squared_error(real, pred))))




###### Main function:
def getPropertiesForImages(images):
    xFound = []
    yFound = []
    widthFound = []
    heightFound = []
    for img in images:
        center,length=getONHProp(img)
        xFound.append(center [0]*5)
        yFound.append(center[1]*5)
        widthFound.append(length[0]*10)
        heightFound.append(length[1]*10)
    return xFound, yFound, widthFound, heightFound

def getPropertiesForImage(image):
    xFound = []
    yFound = []
    widthFound = []
    heightFound = []
    center,length=getONHProp(image)
    xFound.append(center [0]*5)
    yFound.append(center[1]*5)
    widthFound.append(length[0]*10)
    heightFound.append(length[1]*10)
    return xFound, yFound, widthFound, heightFound


########## This part i to do the comparison with manuall data
# images,properties = ExternalStatement()
# xFound, yFound, widthFound, heightFound = getPropertiesForImages(images)
####### save data
# with open("Xcenter.txt", "wb") as fp:  # Pickling
#     pickle.dump(XFound, fp)
# with open("Ycenter.txt", "wb") as fp:  # Pickling
#     pickle.dump(YFound, fp)
# with open("Width.txt", "wb") as fp:  # Pickling
#     pickle.dump(WidthFound, fp)
# with open("Height.txt", "wb") as fp:  # Pickling
#     pickle.dump(HeightFound, fp)

###### load data
# with open("Xcenter.txt", "rb") as fp:   # Unpickling
#     XFound = pickle.load(fp)
# with open("Ycenter.txt", "rb") as fp:  # Unpickling
#     YFound = pickle.load(fp)
# with open("Width.txt", "rb") as fp:   # Unpickling
#     WidthFound = pickle.load(fp)
# with open("Height.txt", "rb") as fp:  # Unpickling
#     HeightFound = pickle.load(fp)
#
#
# for i in range(len(WidthFound)):
#     print(WidthFound[i])
#     print(properties[126+i])
#
#
# def deleteNotDefined(realVal,predictedVal):
#     l=[i for i,v in enumerate(realVal) if v != '']
#     newReal = [realVal[j] for j in l]
#     newPred = [predictedVal[j] for j in l]
#     l1 = [i for i, v in enumerate(newPred) if v != []]
#     newReal2 = [newReal[j] for j in l1]
#     newPred2 = [newPred[j] for j in l1]
#
#     return  newReal2,newPred2
#
# #
# temp=np.copy(properties[126:252])
# realWidth,predWidth = deleteNotDefined(temp,WidthFound)
#
# temp=np.copy(properties[0:126])
# realHeight,predHeight = deleteNotDefined(temp,HeightFound)
#
# temp=np.copy(properties[252:378])
# realX,predX = deleteNotDefined(temp,XFound)
#
# temp=np.copy(properties[378:504])
# realY,predY = deleteNotDefined(temp,YFound)
#
#
#
#
