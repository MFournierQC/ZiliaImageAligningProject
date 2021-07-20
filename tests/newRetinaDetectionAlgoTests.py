
# i = y
# j = x

somme = 0
sommei = 0
sommej = 0
sommei2 = 0
sommej2 = 0

image = grayImage

for i in range(image.shape[0]):
    for j in range(image.shape[1]):
        somme += image[i,j]
        sommei += image[i,j] * i
        sommej += image[i,j] * j
        sommei2 += image[i,j] * (i**2)
        sommej2 += image[i,j] * (j**2)


imoy = sommei / somme
jmoy = sommej / somme

i2moy = sommei2 / sommei
j2moy = sommej2 / sommej

deltai = (i2moy - (imoy)**2)**.5
deltaj = (j2moy - (jmoy)**2)**.5


# deltai = variation verticale
# deltaj = variation horizontale
# imoy = centroïde en y
# jmoy = centroïde en x
