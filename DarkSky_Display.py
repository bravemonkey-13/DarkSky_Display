# Using a Raspberry Pi to display the outside temperature and conditions and inside temperature and humidity on a connected LCD.
# Assumes a 2 row LCD connected using I2C and a DHT sensor on pin 17.
# Scheduled to display between 6am - 10am & 5pm - 10pm on weekdays, 6am - 10pm on weekends and turn the display off otherwise.

import time
import datetime
import I2C_LCD_driver
import Adafruit_DHT
import requests
import json

Ada_Type = Adafruit_DHT.DHT22
Ada_Pin = 17
mylcd = I2C_LCD_driver.lcd()

class LCD:
    LCD_On = True

def GetExternalTemp():
    key = 'd65ba026009ca897ac5b4166d22c7317'
    url = 'https://api.darksky.net/forecast/%s/43.6543,-79.3860?units=ca' % (key)
    # Powered by Darksky
 
    response = requests.get(url)
    weather_data = response.json()
    feelsLike = weather_data['currently']['apparentTemperature']
    Status = weather_data['currently']['summary']

    return round(feelsLike), str(Status)

def GetInternalTemp():
    hum, temp = Adafruit_DHT.read_retry(Ada_Type, Ada_Pin)
    
    return round(hum), round(temp)

def DisplayOnLCD():
        LCD.LCD_On = True

        try:
            out_temp, status = GetExternalTemp()
            humidity, temperature = GetInternalTemp()
        except:
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Retrying",1)
            time.sleep(30)
            return

        mylcd.lcd_clear()
        mylcd.lcd_display_string("OUT %sC" % (str(out_temp)+chr(223)), 1)
        mylcd.lcd_display_string("IN %sC, %d%% HUM" % (str(temperature) + chr(223), humidity), 2)

        statusLength = len(status)

        if statusLength < 8:
            statusLength = 8

        str_pad = " " * statusLength
        status = str_pad + status
        startPos = 7 + len(str(out_temp))
        
        t_end = time.time() + 60 * 5
        while time.time() < t_end:
                for i in range (0, len(status)):
                    lcd_text = status[i:(i+16)]
                    mylcd.lcd_display_string(lcd_text,1,startPos)
                    time.sleep(0.4)
                    mylcd.lcd_display_string(str_pad,1,startPos)
         

def main():
    
    while True:
        date = datetime.date.today()
        today = date.strftime("%a")
        now = datetime.datetime.now()

        if today == "Sat" or today == "Sun" and now.hour >= 6 and now.hour <= 22:
            DisplayOnLCD()
        
        elif now.hour >= 6 and now.hour <= 10 or now.hour >= 17 and now.hour <= 22:
            DisplayOnLCD() 
                
        else:
            if LCD.LCD_On == True:
                mylcd.lcd_clear()
                mylcd.backlight(0)
                LCD.LCD_On = False
            time.sleep(60)         

main()
