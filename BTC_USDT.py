import config
from binance.client import Client
from binance.enums import *
import numpy as np 
import time

cliente = Client(config.API_KEY, config.API_SECRET, tid= "com")

simbolo = "BTC/USDT"
cantidad_orden = 0.00069 # Cantidad a comprar

## ESTE ROBOT ES CON TENDENCIA Y LINEAS MOVILES A LARGO PLAZO ###

def tendencias():
    x = []
    y = []
    sum = 0
    ma48_i = 0

    resp = False

    kline = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_15MINUTE, "12 hour ago UTC")

    if (len(kline) != 60):
        return False
    for i in range(24,60): # de 24 a 60, 36 velas de 15 minutos son 9(horas):30  
        for a in range(i-50,i):
            sum += float(kline[i][4])
        ma48_i = '{:.5f}'.format(sum / 50) # .5 cantidad de decimales que tenemos 0.00059 EJ
        sum = 0
        x.append(i)
        y.append(float(ma48_i))

    modelo = np.polyfit(x,x,1)
    if (modelo[0]>0):
        resp = True
    return resp

def _ma48():
     
     ma50_local = 0
     sum = 0

     kline = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_15MINUTE, "12 hour ago UTC")

     if (len(kline)== 48):
          for i in range (0,48):
            sum += float(kline[i][4]) # 4 Es el precio de cierre de la vela 
          ma48_local = sum / 48
        
     return ma48_local


while 1:
    ordenes = cliente.get_open_orders(symbol = simbolo)
    print("ordenes abiertas") # Si hay ordenes abiertas no comprar
    print(ordenes)

    if(len(ordenes) !=0):
        print("Existen ordenes abiertas, no comprar ")
        time.sleep(10)
        continue

    # obtener el precio actual de la moneda

    list_de_tickers = cliente.get_all_tickers()
    for tick in list_de_tickers:
        if tick['symbol'] == simbolo:
          precio_simbolo = float(tick['price']) 

    ma48 = _ma48()
    if (ma48 == 0): continue

    print("------>" + simbolo + "<------")
    print("PRECIO ACTUAL DE MA48" + str('{:.8f}'.format(simbolo))) # .8 cantidad de decimales del simbolo
    print("PRECIO ACTUAL DE LA MONEDA" + str('{:.8f}'.format(precio_simbolo)))
    print("Precio para comprar" + str('{:.8f}'.format(ma48*0.995)))

    if(not tendencias()):
        print("Tendencia bajista no comprar")

        time.sleep(15)
        continue
    else:
        print("Tendencia en alza, comprar")

    if (precio_simbolo > ma48*0.995):
        print("Comprando")

    orden = cliente.order_market_buy(
        #API = LOCAL
            symbol = simbolo,
            quantity = cantidad_orden

        )
    
    time.sleep(5)

    # Orden oco -->

    ordenoco = cliente.create_oco_order(
            symbol = simbolo,
            side = SIDE_SELL,
            stop_limite_precio = str('{:.8f}'.format(precio_simbolo*0.995)),
            stop_limit_inforce = TIME_IN_FORCE_GTC,
            quantity = cantidad_orden*0.999, # Lo que bainance cobra, o sino nos da un error insuficent FOUND
            stopprecio = str('{:.8f}'.format(precio_simbolo*0.995)),
            price = str('{:.8f}'.format(precio_simbolo*0.995))
        )
    time.sleep(20) # robot a dormir porque abrio una orden, dejar el mercado operar




















