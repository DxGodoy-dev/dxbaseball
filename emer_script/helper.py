import statsapi
import datetime as dt

today = dt.date.today()
consulta = statsapi.schedule(today)
print(consulta)