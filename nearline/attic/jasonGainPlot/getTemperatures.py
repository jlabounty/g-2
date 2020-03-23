import pandas
import sys
import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
import calendar

if(len(sys.argv) < 3):
    timeStart = "2018-05-26 15:00:34" 
    timeEnd =  "2018-05-26 15:49:34.459428"
else:
    timeStart = str(sys.argv[1])
    timeEnd = str(sys.argv[2])

if(len(sys.argv) > 3):
	trailText = str(sys.argv[3])
else:
	trailText = ""

print("Running with times:", timeStart, timeEnd)

if(trailText == "_24h"):
    os.system('PGPASSWORD=gm2_4_reader psql -U gm2_reader -d gm2_online_prod -h ifdbprod.fnal.gov -p 5452 -c "\copy (select * from g2sc_values where time > \''+timeStart+'\' and time < \''+timeEnd+'\' ) to \'./test.csv\' with CSV DELIMITER \'|\';" ' )
else:
    os.system('PGPASSWORD=gm2_4_reader psql -U gm2_reader -d gm2_online_prod -h ifdbprod.fnal.gov -p 5452 -c "\copy (select * from g2sc_values where time > \''+timeStart+'\' and time < \''+timeEnd+'\' order by random() limit 2000000 ) to \'./test.csv\' with CSV DELIMITER \'|\';" ' )

print("Database Accessed. Making vectors")

tempVec = []
timeFormatTemp = "%Y-%m-%d %H:%M:%S.%f" # 2018-05-12 09:51:38.169989 |

with open("./test.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='|')
    line_count = 0
    for row in csv_reader:
        if(not('calo' in row[1])):
            continue
        try:
            caloNum = int((row[1].split("calo"))[1].split('temps')[0])
            #print(caloNum)
            ding = []
            for x in row[2][1:-1].split(','):
                if float(x) > 0 and float(x) < 100:
                    ding.append(float(x))
                else:
                    ding.append(float('nan'))
            
            #print(ding)
            vec = [caloNum, ding, np.nanmean(ding), 
                            time.strptime(row[3], timeFormatTemp), 
                            row[3],
                            calendar.timegm(time.strptime(row[3], timeFormatTemp)) ]
            for x in ding:
                #print(x)
                vec.append(float(x))
            tempVec.append(vec)
        except:
            print("ERROR: ", row)

            line_count += 1
            if(line_count > 50):
                break


print("Creating dataframe") 

df = pandas.DataFrame(tempVec, columns=['calo','temps','avgtemp','timefull','timestring','time','xtal0', 'xtal1', 'xtal2', 'xtal3', 
                                        'xtal4', 'xtal5', 'xtal6', 'xtal7', 'xtal8', 'xtal9', 'xtal10', 'xtal11', 'xtal12', 'xtal13', 
                                        'xtal14', 'xtal15', 'xtal16', 'xtal17', 'xtal18', 'xtal19', 'xtal20', 'xtal21', 'xtal22', 
                                        'xtal23', 'xtal24', 'xtal25', 'xtal26', 'xtal27', 'xtal28', 'xtal29', 'xtal30', 'xtal31', 
                                        'xtal32', 'xtal33', 'xtal34', 'xtal35', 'xtal36', 'xtal37', 'xtal38', 'xtal39', 'xtal40', 
                                        'xtal41', 'xtal42', 'xtal43', 'xtal44', 'xtal45', 'xtal46', 'xtal47', 'xtal48', 'xtal49', 
                                        'xtal50', 'xtal51', 'xtal52', 'xtal53'])


df.timefull = pandas.to_datetime(df.timestring)
#df.sort_values(by=['timefull'])

print(df.head())


timeFormatTemp = "%Y-%m-%d %H:%M:%S"
runVec = []
with open("./runsByUnixTime.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='|')
    line_count = 0
    for row in csv_reader:
        try:
            runNum = int(row[0])

            vec = [runNum,
                   row[1],
                   calendar.timegm(time.strptime(row[1], timeFormatTemp)) ,
                   row[3],
                   calendar.timegm(time.strptime(row[3], timeFormatTemp)) ]

            runVec.append(vec)
        except:
            print("ERROR: ", row)

            line_count += 1
            if(line_count > 50):
                break

runVec.sort()
dfruns = pandas.DataFrame(runVec, columns=['run', 'timeStartString', 'timeStart', 'timeEndString', 'timeEnd'] )
print(dfruns.head())

dfconstants = pandas.read_csv("./nearlineConstantsByRun.csv", header=None, names=['run','calo','allXtalAvg','xtal0', 'xtal1', 'xtal2', 'xtal3', 
                                        'xtal4', 'xtal5', 'xtal6', 'xtal7', 'xtal8', 'xtal9', 'xtal10', 'xtal11', 'xtal12', 'xtal13', 
                                        'xtal14', 'xtal15', 'xtal16', 'xtal17', 'xtal18', 'xtal19', 'xtal20', 'xtal21', 'xtal22', 
                                        'xtal23', 'xtal24', 'xtal25', 'xtal26', 'xtal27', 'xtal28', 'xtal29', 'xtal30', 'xtal31', 
                                        'xtal32', 'xtal33', 'xtal34', 'xtal35', 'xtal36', 'xtal37', 'xtal38', 'xtal39', 'xtal40', 
                                        'xtal41', 'xtal42', 'xtal43', 'xtal44', 'xtal45', 'xtal46', 'xtal47', 'xtal48', 'xtal49', 
                                        'xtal50', 'xtal51', 'xtal52', 'xtal53'], sep='|')

print("Plotting!")

'''

fig, ax = plt.subplots(figsize=(15,6))
for calo in range(1,25):
    plt.plot(df["time"].loc[df['calo'] == calo], df['avgtemp'].loc[df['calo'] == calo], ".", label='calo '+str(calo))
plt.title("Average SiPM Temperatures in All Calos ["+timeStart+" < t < "+timeEnd+"]")
plt.xlabel("UNIX Time")
plt.ylabel("Temperature [Degrees Centigrade]")
plt.legend(ncol=8)
plt.draw()
plt.close()



fix, ax = plt.subplots(figsize=(15,6))
for calo in range(1,25):
    plt.plot((df["timefull"].loc[df['calo'] == calo]), df['avgtemp'].loc[df['calo'] == calo],".", label='calo '+str(calo))
plt.title("Average SiPM Temperatures in All Calos ["+timeStart+" < t < "+timeEnd+"]")
plt.xlabel("Time")
plt.ylabel("Temperature [Degrees Centigrade]")
plt.legend(ncol=8)
plt.savefig("./CaloTemperatures_SameScale"+trailText+".png",bbox_inches="tight")
plt.draw()
plt.close()



width = 6
fig, ax = plt.subplots(width,4,figsize=(30,15),sharex = True)
for calo in range(1,25):
    i = calo -1
    axi = ax[i % width][int(i/width)]
    axi.plot((df["timefull"].loc[df['calo'] == calo]), df['avgtemp'].loc[df['calo'] == calo], ".", label='calo '+str(calo))
    axi.set_title("Calo "+str(calo))
plt.tight_layout()
plt.suptitle("Average SiPM Temperatures in All Calos ["+timeStart+" < t < "+timeEnd+"]", fontsize=18, y = 1.01)

plt.savefig("./CaloTemperatures_IndividualScales"+trailText+".png",bbox_inches="tight")

plt.draw()
plt.close()

width = 9
height = 6

for calo in range(1,25):
    fig, ax = plt.subplots(height,width,figsize=(30,15),sharex = True)
    for xtal in range(54):
        i = xtal
        axi = ax[int((53-i)/width)][(53 - i) % width]
        axi.plot(df["timefull"].loc[df['calo'] == calo], df['xtal'+str(xtal)].loc[df['calo'] == calo], ".")
        axi.set_title("Xtal "+str(xtal))

    for ax in fig.axes:
        matplotlib.pyplot.sca(ax)
        plt.xticks(rotation=60)
        ax.grid(True,axis="x")
        
    plt.suptitle("Average SiPM Temperatures in Calo "+str(calo)+" ["+timeStart+" < t < "+timeEnd+"]", fontsize=18, y = 1.01)
    plt.tight_layout()
    plt.savefig("./CrystalTemperatures_Calo"+str(calo).zfill(2)+"_IndividualScales"+trailText+".png",bbox_inches="tight")
    
    plt.draw()
    plt.close()

for calo in range(1,25):
    fig, ax = plt.subplots(height,width,figsize=(30,15),sharex = True, sharey = True)
    for xtal in range(54):
        i = xtal
        axi = ax[int((53-i)/width)][(53 - i) % width]
        axi.plot(df["timefull"].loc[df['calo'] == calo], df['xtal'+str(xtal)].loc[df['calo'] == calo], ".")
        axi.set_title("Xtal "+str(xtal))

    for ax in fig.axes:
        matplotlib.pyplot.sca(ax)
        plt.xticks(rotation=60)
        ax.grid(True,axis="x")
        
    plt.suptitle("Average SiPM Temperatures in Calo "+str(calo)+" ["+timeStart+" < t < "+timeEnd+"]", fontsize=18, y = 1.01)
    plt.tight_layout()
    plt.savefig("./CrystalTemperatures_Calo"+str(calo).zfill(2)+trailText+".png",bbox_inches="tight")
    
    plt.draw()
    plt.close()

#plt.show()

'''

print(df.head())
print(dfconstants.head())

runVec = []

for i, row in dfruns.iterrows():
	#print(row)
	runNum = row['run']
	timeStart = row['timeStart']
	timeEnd = row['timeEnd']
	#print(runNum, timeStart, timeEnd)
	constantVec = []

	dfi = df.loc[df['time'] > timeStart].loc[df['time'] < timeEnd]
	if(len(dfi) > 0): 
		print(row)
		print("Entries in DF:", len(dfi))
		for calo in range(1,25):
			dfi2 = dfi.loc[dfi['calo'] == calo]
			xtalsMeanCaloi = []
			for xtal in range(54):
				xtalMean = np.mean( dfi2['xtal'+str(xtal)] )
				xtalsMeanCaloi.append( xtalMean )
			ding = [runNum, calo]
			for x in xtalsMeanCaloi:
				ding.append(x)
			runVec.append( ding )

#print(runVec)

dfconstantsByRun = pandas.DataFrame(runVec, columns=['run', 'calo','xtal0', 'xtal1', 'xtal2', 'xtal3', 
                                        'xtal4', 'xtal5', 'xtal6', 'xtal7', 'xtal8', 'xtal9', 'xtal10', 'xtal11', 'xtal12', 'xtal13', 
                                        'xtal14', 'xtal15', 'xtal16', 'xtal17', 'xtal18', 'xtal19', 'xtal20', 'xtal21', 'xtal22', 
                                        'xtal23', 'xtal24', 'xtal25', 'xtal26', 'xtal27', 'xtal28', 'xtal29', 'xtal30', 'xtal31', 
                                        'xtal32', 'xtal33', 'xtal34', 'xtal35', 'xtal36', 'xtal37', 'xtal38', 'xtal39', 'xtal40', 
                                        'xtal41', 'xtal42', 'xtal43', 'xtal44', 'xtal45', 'xtal46', 'xtal47', 'xtal48', 'xtal49', 
                                        'xtal50', 'xtal51', 'xtal52', 'xtal53'])

print(dfconstantsByRun.head())

runMin = dfconstantsByRun['run'].min()
runMax = dfconstantsByRun['run'].max()
width = 9
height = 6

for calo in range(1,2):
	fig, ax = plt.subplots(height,width,figsize=(30,15),sharex = True)
	dfTempsi = dfconstantsByRun.loc[dfconstantsByRun['calo'] == calo]
	dfConsti = dfconstants.loc[dfconstants['calo'] == calo].loc[dfconstants['run'] > runMin - 1].loc[dfconstants['run'] < runMax + 1]
	for xtal in range(54):
		i = xtal
		axi = ax[int((53-i)/width)][(53 - i) % width]
		axi.set_title("Xtal "+str(xtal))

		axi.plot(dfTempsi['run'], dfTempsi['xtal'+str(xtal)]/np.mean(dfTempsi['xtal'+str(xtal)]), label = 'Temperatures')
		axi.plot(dfConsti['run'], dfConsti['xtal'+str(xtal)]/np.mean(dfConsti['xtal'+str(xtal)]), label = 'Gain Contstants')
	for ax in fig.axes:
		matplotlib.pyplot.sca(ax)
		plt.xticks(rotation=60)
		ax.grid(True,axis="x")

#plt.suptitle("Average SiPM Temperatures in Calo "+str(calo)+" ["+timeStart+" < t < "+timeEnd+"]", fontsize=18, y = 1.01)
plt.tight_layout()
plt.legend()
plt.show()
plt.savefig("./ding.png",bbox_inches="tight")
plt.close()

