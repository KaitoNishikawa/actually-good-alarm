originalCounts = []
croppedCounts = []
originalHR = []
croppedHR = []
time = 24500

with open('./outputs/features2/5_count_feature.out', 'r') as file:
    for line in file:
        originalCounts.append(float(line))

with open('./outputs/features2/3_count_feature.out', 'r') as file:
    for line in file:
        croppedCounts.append(float(line))
    
with open('countDifferences_' + str(time) + 's_2.txt', 'w') as file:
    for index, i in enumerate(croppedCounts[:-10]):
        file.write(str(abs(originalCounts[index] - croppedCounts[index]) * 100) + '\n')



with open('./outputs/features2/5_hr_feature.out', 'r') as file:
    for line in file:
        originalHR.append(float(line))

with open('./outputs/features2/3_hr_feature.out', 'r') as file:
    for line in file:
        croppedHR.append(float(line))
    
with open('hrDifferences_' + str(time) + 's_2.txt', 'w') as file:
    for index, i in enumerate(croppedHR[:-10]):
        file.write(str(abs(originalHR[index] - croppedHR[index]) * 100) + '\n')