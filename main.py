from Classes import ChargingUnit,ElectricVehicle
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os 

def simulateCharging(ev,cu,startTime,endTime,connectionTime, disconnectionTime,interval):
    time = startTime
    chargingPower = 0
    energyCharged = 0
    initialSoc = ev.stateOfCharge
    i = 0
    data = [[time,chargingPower,ev.stateOfCharge,energyCharged]]
    while time < endTime:
        if time >= connectionTime and time <= disconnectionTime:
            ev.connectionStatus = True
            cu.connectionStatus = True
            chargingPower = min(ev.maxPower,cu.maxPower)

            lastStep = int(((disconnectionTime - connectionTime).total_seconds())/(interval.total_seconds()))

            while time < disconnectionTime:
                if min(ev.maxPower,cu.maxPower)*((interval.total_seconds())/3600)*(i+2)+(initialSoc/100)*ev.batteryCapacity > ev.batteryCapacity or i >= lastStep-2: #Checking if the constant power will overcharge the battery in the next steps
                    chargingPower = min(ev.maxPower,cu.maxPower)*((disconnectionTime - time).total_seconds())/((disconnectionTime - connectionTime).total_seconds()) # Linear decrasing 
                if abs(100 - ev.stateOfCharge) < 0.1 or ev.stateOfCharge == 100: #Considering a 0.1 tolerance for discrete approach
                    chargingPower = 0
                energyCharged = chargingPower*(interval.total_seconds()/3600)
                ev.stateOfCharge += (energyCharged/ev.batteryCapacity)*100
                ev.stateOfCharge = min(ev.stateOfCharge,100)
                time += interval
                i += 1
                data.append([time,chargingPower,ev.stateOfCharge,energyCharged])
        chargingPower = 0
        ev.connectionStatus = False
        cu.connectionStatus = False 
        time+=interval
        data.append([time,chargingPower,ev.stateOfCharge,energyCharged])
    return pd.DataFrame(data, columns=["Timestamp", "Charging Power (kW)", "SOC (%)", "Net Energy Charged (kWh)"])

#Simulation parameters

startTime = datetime.strptime("09:00", "%H:%M")
endTime = datetime.strptime("21:00", "%H:%M")
connectionTime = input("Connection Time: ")
disconnectionTime = input("Disconnection Time: ")
connectionTime = datetime.strptime(connectionTime, "%H:%M")
disconnectionTime = datetime.strptime(disconnectionTime, "%H:%M")
interval = timedelta(minutes=15)

ev = ElectricVehicle.EletricVehicle()
cu = ChargingUnit.ChargingUnit()

#Setting path for data exports 
base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "Exports")
json_path = os.path.join(output_dir, "charging_data.json")
xlsx_path = os.path.join(output_dir, "charging_data.xlsx")
png_path = os.path.join(output_dir, "soc_plot.png")

#Running Simulation
df = simulateCharging(ev,cu,startTime,endTime,connectionTime,disconnectionTime,interval)

#Results
df.to_json(json_path, orient="records")
df.to_excel(xlsx_path,index=False)
plt.figure(figsize=(10, 5))
plt.plot(df["Timestamp"], df["SOC (%)"], marker='o', linestyle='-')
plt.xlabel("Time")
plt.ylabel("SOC (%)")
plt.title("SOC Trajectory")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.xticks(rotation=45) 
plt.grid()
plt.savefig(png_path)
plt.show()
