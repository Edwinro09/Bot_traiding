import config
from binance.client import Client
from binance.enums import *
import time
import numpy as np

cliente = Client(config.API_KEY, config.API_SECRET, tld='com')

simbolo = 'RVNUSDT'
cantidadOrden = 100 # cantidad a comprar

#### ESTE ROBOT CON TENDENCIA Y LINEAS MOVILES #### largo plazo

def tendencia():
    x = []
    y = []
    sum = 0
    ma48_i = 0

    resp = False

    klines = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_15MINUTE, "18 hour ago UTC")

    if (len(klines) != 72):
        
        return False
    for i in range (1,72): # de 24 a 60, 36 velas de 15 minutos son 9hs media

        for j in range (i-72,i): 
          sum = sum + float(klines[i][4])
        ma48_i = '{:.8f}'.format(sum /72)
        sum = 0
        x.append(i)
        y.append(float(ma48_i))

    modelo = np.polyfit(x,y,1)
    if (modelo[0]>0):
        resp = True
    

    return resp
    


def _ma48_():

    ma48_local = 0
    sum = 0

    klines = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_15MINUTE, "12 hour ago UTC")

    if(len(klines)==48):
        for i in range (0,48):
            sum = sum +float(klines[i][4]) # 4 precio de cierre de la vela
        
        ma48_local = sum / 48

    return ma48_local

while 1:
    ordenes = cliente.get_open_orders(symbol=simbolo)
    print("Ordenes actuales abiertas: ") #Si hay ordenes abiertas no compra
    print(ordenes)

    if(len(ordenes) !=0):
        print("Existen ordenes abiertas, no se compra")
        time.sleep(10)
        continue

    # traer el precio actual de la moneda o simbolo

    list_of_tickers = cliente.get_all_tickers()
    for tick_2 in list_of_tickers:
        if tick_2['symbol'] == simbolo:
            PrecioSimbolo = float(tick_2['price'])
    # price

    ma48 = _ma48_()
    if (ma48 == 0): continue

    print("--------" + simbolo + "---------")
    print(" Precio actual de MA48 " + str('{:.8f}'.format(ma48))) #el .8 es la cantidad de decimales que no trae el simbolo 
    print(" PRECIO Actual de la moneda " + str('{:.8f}'.format(PrecioSimbolo)))
    print(" Precio a comprar " + str('{:.8f}'.format(ma48*0.995)))

    if (not tendencia()): 
        print ("Tendencia bajista, no se realizan ordenes de compra")

        time.sleep(10)
        continue
    else:
        print("Tendencia en ALZA, comprando si no hay ordenes abiertas")

    if(PrecioSimbolo > ma48*0.995):
        print("COMPRANDO")

    orden = cliente.order_market_buy(
        #API =   local
            symbol = simbolo,
            quantity = cantidadOrden
            
        )
    time.sleep(5)

    #Pongo la orden OCO (one cancells other)

    info = cliente.get_symbol_info(simbolo)
    
    print(info['filters'][2]['minQty'])

    ordenOCO = cliente.create_oco_order(
            symbol = simbolo,
            side = SIDE_SELL,
            stopLimitPrice = str('{:.5f}'.format(PrecioSimbolo*0.985)),
            stopLimitTimeInForce = TIME_IN_FORCE_GTC,
            quantity = cantidadOrden*0.999, # BINANCE cobra un fee, tarifa. Sino va a tirar un error de insuficent FOUNDS.
            stopPrice = str('{:.5f}'.format(PrecioSimbolo*0.99)),
            price = str('{:.5f}'.format(PrecioSimbolo*1.01)),
            )
    
    time.sleep(20) #mando el robot a dormir porque EN TEORIA abrio un orden, dejamos que el mercado opere.

    # FAQ

    # Signature for this request is not valid. API o secret estan mal. 
    # Invalid symbol: controlar que este bien escrito el simbolo. 
    # PRICE_FILTER. acomodo los decimales en la orden OCO
    # Min_NOTIONAL: evaluo con info cuanto es el minimo que se puede comprar
    # The relationship of the prices for the orders is not correct. 
