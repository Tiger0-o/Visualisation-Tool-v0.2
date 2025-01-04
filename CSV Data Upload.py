import csv, time, random

csv_file = "C:\\Users\\zhaoc\\Downloads\\LiDAR Program File\\output.csv"
header = ['radius', 'yaw_degrees', 'pitch_degrees']

variableDict = {'yawDegrees': 0, 'pitchDegrees': 0, 'measuredDistance': 0}
turningDict = {'turningDegree': 1, 'pitchLimit': 360, 'yawLimit': 90}

with open(csv_file, 'w') as file:
    file.write('')

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)

    while variableDict['yawDegrees'] <= turningDict['yawLimit']:
        variableDict['pitchDegrees'] = 0

        while variableDict['pitchDegrees'] <= turningDict['pitchLimit']:
            r = round(1, 1)
            yaw = round(variableDict['yawDegrees'], 1)
            pitch = round(variableDict['pitchDegrees'], 1)

            writer.writerow([r, yaw, pitch])
            variableDict['pitchDegrees'] += turningDict['turningDegree']
        variableDict['yawDegrees'] += turningDict['turningDegree']
            
        
    


        
