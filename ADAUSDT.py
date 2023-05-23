import config
import math
from binance.client import Client
from binance.enums import *
import time
import numpy as np
from colorama import init 
from colorama import Fore, Back, Style
import math
init()


cliente = Client(config.API_KEY, config.API_SECRET, tld='com')

simbolo = 'ADAUSDT'
simboloBalnce = 'ADA'
cantidadOrden = 66 # cantidad a comprar (Varias monedasd de BTC tienen error LOTSIZE por compras menores a 20 USD)

decimales = '{:.4f}'


def _ma5_ ():
    ma5_local = 0
    sum = 0

    klines = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_5MINUTE, "25 minute ago UTC")

    if(len(klines)==5):
        for i in range (0,5):
            sum = sum +float(klines[i][4]) # 4 precio de cierre de la vela
        
        ma5_local = sum / 5

    return ma5_local

def _ma10_ ():
    ma10_local = 0
    sum = 0

    klines = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_5MINUTE, "50 minute ago UTC")

    if(len(klines)==10):
        for i in range (0,10):
            sum = sum +float(klines[i][4]) # 4 precio de cierre de la vela
        
        ma10_local = sum / 10

    return ma10_local


def _ma20_ ():
    ma20_local = 0
    sum = 0

    klines = cliente.get_historical_klines(simbolo, Client.KLINE_INTERVAL_5MINUTE, "100 minute ago UTC")

    if(len(klines)==20):
        for i in range (0,20):
            sum = sum +float(klines[i][4]) # 4 precio de cierre de la vela
        
        ma20_local = sum / 20

    return ma20_local

while 1:

    ## Calculamos el balance en cuenta para poner orden OCO exacta y evitar LOTSIZA
    sum_simbolo = 0.0 
    balances = cliente.get_account()
    for _balance in balances["balances"]:
        asset = _balance["asset"]
        if float(_balance["free"]) != 0.0 or (_balance["locked"]) != 0.0:
            try:
                simbolo_quantity = float(_balance["free"]) + float(_balance["locked"])
                if asset == simboloBalnce:
                    sum_simbolo += simbolo_quantity
                else:
                    _price = cliente.get_symbol_ticker(symbol=asset + simboloBalnce)
                    sum_simbolo += simbolo_quantity * float(_price["price"]) 
            except:
                pass
        current_simbolo_price = cliente.get_symbol_ticker(symbol=simbolo)["price"] 
        own_usd = sum_simbolo * float(current_simbolo_price)
        print("Balance en billetera => " + simboloBalnce + "%.8f ==" %sum_simbolo, end="")
        time.sleep(100)

                                                          

    requestMinQtOrden = cliente.get_symbol_info(simbolo)
    ordenes = cliente.get_open_orders(symbol=simbolo)
    print(Fore.BLUE + "Ordenes actuales abiertas") # si devuelve [] esta vacio

    if(len(ordenes) != 0):
        print(len(ordenes))
        print("Cantidad  a vender " + str(math.floor(sum_simbolo)))
        print("Precio de venta si BAJA  " + ordenes[0]['price'])
        print("Precio de venta si SUBE  " + ordenes[1]['price'])
        time.sleep(20) # Mando el robot a dormir porque EN TEORIA abrio una orden 
        continue 

    if(len(ordenes)!= 0):
        print(Fore.RED + "Hay ordenes abiertas")
        time.sleep(10)
        continue

    # Tener el precio del token 
    list_of_ticker = cliente.get_all_tickers()
    for tick_2 in list_of_ticker:
        if tick_2['symbol'] == simbolo:
            symbolPrice = float(tick_2['price'])
    # Obtenemos el precio

    ma5 = _ma5_()
    ma10 = _ma10_()
    ma20 = _ma20_()

    if(ma20 == 0): continue

    requestMinQtOrden = cliente.get_symbol_info(simbolo)
    print("Cantidad minima de ordenes de compra es: " + requestMinQtOrden['filters'][2]['minQty'])
    minQtOrder = float(requestMinQtOrden['filters'][2]['minQty'])

    if(minQtOrder !=10):
        print("ordenes acepta decimales")
        orden_local = '{:.4f}'.format(cantidadOrden*0.999)
    else:
        print("Ordenes acepta solo numeros enteros")
        orden_local = '{:.0f}'.format(cantidadOrden*0.9990)

    
    
    
    # Importante los decimales de la moneda 

    print(Fore.BLUE + "--------" + simbolo + "---------")
    print("**********************************")
    print(" Precio actual de "+ simbolo + " es: " + str(decimales.format(symbolPrice))) #el .8 es la cantidad de decimales que no trae el simbolo 
    print(Fore.GREEN + "Precio MA5" + str(decimales.format(ma5)))
    print(Fore.YELLOW + "Precio MA10" + str(decimales.format(ma10)))
    print(Fore.RED + "Precio MA20" + str(decimales.format(ma20)))
    print("Precio en que se va a comprar" + str(decimales.format(ma20*0.995)))
    if(symbolPrice > ma5 and ma5 > ma10 and ma10 > ma20):
        print(Fore.GREEN + "Comprando si no hay ordenes abiertas")

    # ORDENES DE PRUEBA
        #order = cliente.create_test_order(
        #symbol = simbolo,
        #side = SIDE_BUY,
        #type = ORDER_TYPE_LIMIT,
        #timeInforse = TIME_IN_FORCE_GTC,
        #quantity = cantidadOrden,
        #price = str(decimales.format(symbolPrice*1.02)),
        #)
    
       # orders = cliente.get_all_orders(symbol=simbolo)
       # print(orders)
        orden = cliente.order_market_buy(
            #API =   local
                symbol = simbolo,
                quantity = cantidadOrden
            
            )
        time.sleep(5)


        print("Haciendo orden OCO...")
        print("Precio a comprar >    " + str(decimales.format(symbolPrice*1.01)))

        ordenOCO = cliente.create_oco_order(
                symbol = simbolo,
                side = SIDE_SELL,
                stopLimitPrice = str(decimales.format(symbolPrice*0.985)),
                stopLimitTimeInForce = TIME_IN_FORCE_GTC,
                ## Error LOS SIZE es porque no soporta decimales en quantity
                quantity =  str(math.floor(sum_simbolo)), # BINANCE cobra un fee, tarifa. Sino va a tirar un error de insuficent FOUNDS.
                stopPrice = str(decimales.format(symbolPrice*0.99)),
                price = str(decimales.format(symbolPrice*1.01)),
                )
    
        time.sleep(20) #mando el robot a dormir porque EN TEORIA abrio un orden, dejamos que el mercado opere.


    else:
        print(Fore.RED + "No se cumple las condiciones")
        time.sleep(20)

    # Fin ordenes prueba