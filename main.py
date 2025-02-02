from Classes import ChargingUnit,ElectricVehicle
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os 

def simulateCharging(ev,cu,startTime,endTime,connectionTime, disconnectionTime,interval):
    time = startTime
    chargingPower = min(ev.maxPower,cu.maxPower)
    energyCharged = 0
    data = [[time,chargingPower,ev.stateOfCharge,energyCharged]]
    i = 0
    while time < endTime:
        if time >= connectionTime and time <= disconnectionTime:
            while time < disconnectionTime:
                if chargingPower*(interval.total_seconds()/3600)*(i+3) > ev.batteryCapacity:
                    chargingPower = (100 - ev.stateOfCharge)*ev.batteryCapacity/(interval.total_seconds()/36)
                elif ev.stateOfCharge >= 100:
                    chargingPower = 0
                energyCharged = chargingPower*(interval.total_seconds()/3600)
                ev.stateOfCharge += (energyCharged/ev.batteryCapacity)*100
                time += interval
                data.append([time,chargingPower,ev.stateOfCharge,energyCharged])
                i += 1 
        time+=interval
        data.append([time,chargingPower,ev.stateOfCharge,energyCharged])
    return pd.DataFrame(data, columns=["Timestamp", "Charging Power (kW)", "SOC (%)", "Net Energy Charged (kWh)"])

#Simulation parameters

startTime = datetime.strptime("09:00", "%H:%M")
endTime = datetime.strptime("21:00", "%H:%M")
connectionTime = input()
disconnectionTime = input()
connectionTime = datetime.strptime(connectionTime, "%H:%M")
disconnectionTime = datetime.strptime(disconnectionTime, "%H:%M")


interval = timedelta(minutes=15)
ev = ElectricVehicle.EletricVehicle()
cu = ChargingUnit.ChargingUnit()

df = simulateCharging(ev,cu,startTime,endTime,connectionTime,disconnectionTime,interval)


base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "Exports")
json_path = os.path.join(output_dir, "charging_data.json")
xlsx_path = os.path.join(output_dir, "charging_data.xlsx")
png_path = os.path.join(output_dir, "soc_plot.png")

df.to_json(json_path, orient="records")
df.to_excel(xlsx_path,index=False)



plt.figure(figsize=(10, 5))
plt.plot(df["Timestamp"], df["SOC (%)"], marker='o', linestyle='-')
plt.xlabel("Time")
plt.ylabel("SOC (%)")
plt.title("SOC Trajectory")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.xticks(rotation=45) #Better visualization 
plt.grid()
plt.savefig(png_path)
plt.show()
