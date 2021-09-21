from experiment import *
import hashlib
import sys
import re  

# Use with : find . -name "*csv" -exec python3 formatspectroforimport.py {} \; > importall.csv
if len(sys.argv) > 1:
    filepath = sys.argv[1]
else:
    filepath = sys.stdin

# data = DataFile(filepath=filepath, delimiter=',', hasHeader=False, skipLines=10)

text_file = open(filepath, "br")
hash = hashlib.md5(text_file.read()).hexdigest()
text_file.close()

# Using SQL commands is 1000x slower than using a CSV
# No spaces after comma!
# print("wavelength,intensity,column,md5")

text_file = open(filepath, "r")

lines = text_file.read().splitlines()

for line in lines:
    if re.match(r'^(\d+),', line):
        values = line.split(',')
        wavelength = values[0]

        # values.pop(0) # Index
        values.pop(0) # wavelength
        values.pop(0) # ref
        values.pop(0) # bg

        for col, intensity in enumerate(values):
            print(f'{wavelength},{intensity},null,{filepath},raw {col},{hash}')
# # Must be wavelength, intensity, fileId, column, path, md5, backgroundCorrected, normalized
# for curve in data.curves:
#     nPts = len(curve.x)
#     for i in range(nPts):
#         print(f"{curve.x[i]},{curve.y[i]},NULL,{curve.label},NULL,{hash},NULL,NULL")
