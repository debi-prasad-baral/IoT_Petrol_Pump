#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import Adafruit_CharLCD as LCD
from urllib.request import urlopen
from datetime import datetime
from smbus import SMBus
import math
import os, errno
import time
import subprocess
import requests
  
GPIO.setwarnings(False)
GPIO.cleanup()

site = 'http://www.iotgecko.com/IOTHit.aspx?Id=dbaral29@gmail.com&Pass=4542&Data='

# Raspberry Pi pin configuration:
lcd_rs        = 21  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 20
lcd_d4        = 16
lcd_d5        = 26
lcd_d6        = 19
lcd_d7        = 13

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows)

pump = 3
button = 4
main = True

GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pump, GPIO.OUT)
GPIO.output(pump, True)

reader = SimpleMFRC522()

def check_connectivity():
    try:
        r = requests.get(site)
        response = str(r.content)
        print(str(response))
        print(response[577:582])
        return (str(response[577:582]))
    except:
        return False

def get_key():
    kp = keypad()
    digit = None
    while digit == None:
        digit = kp.getKey()
    # Print result
    #print (digit)
    return digit

def get_ID():
    id, text = reader.read()
    print(str(id))
    lcd.message(str(id))
    if id == 1062576087691:
        return 1
    elif id == 768969218688:
        return 2
    elif id == 574225760880:
        return 3
    elif id == 32437330562:
        return 4
    elif id == 308071129831:
        return 5

class keypad():
    def __init__(self, columnCount = 3):
        GPIO.setmode(GPIO.BCM)

        # CONSTANTS 
        if columnCount is 3:
            self.KEYPAD = [
                [1,2,3],
                [4,5,6],
                [7,8,9],
                ["*",0,"#"]
            ]

            self.ROW         = [14,15,18,27]
            self.COLUMN      = [23,22,12]
        
        elif columnCount is 4:
            self.KEYPAD = [
                [1,2,3,"A"],
                [4,5,6,"B"],
                [7,8,9,"C"],
                ["*",0,"#","D"]
            ]

            self.ROW         = [18,23,24,25]
            self.COLUMN      = [4,17,22,21]
        else:
            return
     
    def getKey(self):
         
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i
                 
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0 or rowVal >3:
            self.exit()
            return
         
        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
         
        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)
 
        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal <0 or colVal >2:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
         
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)


amount = []

while GPIO.input(button) == True:    
    lcd.clear()
    lcd.message(" IoT based RFID \n   Petrol Pump  ")
    time.sleep(2)
    lcd.clear()
    lcd.message("     using      \n  Raspberry Pi  ")
    time.sleep(2)
    lcd.clear()
    lcd.message('Connecting to \nInternet...')
    time.sleep(2)
    t1 = datetime.now()
    
    while not check_connectivity():
        t2 = datetime.now()
        delta = t2 - t1
        time_elapse = delta.total_seconds()
        if time_elapse > 10:
            lcd.clear()
            lcd.message('Error: Check\nyour Internet!')
            main = False
            lcd.clear()
            lcd.message("Press 'RESET' to\nRestart")
            while GPIO.input(button) == True:
                None
            break
        else:
            main = True
            
    lcd.clear()
    lcd.message('Connected!')
    time.sleep(2)
    lcd.clear()
    lcd.message("Scan your Card:\n")

    t1 = datetime.now()
    while main == True:
        print('ok')
        user = get_ID()
        print(user)
        time.sleep(2)
        lcd.clear()
        lcd.message("User " + str(user) + " detected!")
        time.sleep(2)


        lcd.clear()
        lcd.message("Enter amount: \n")
        for i in range(3):
            amount.append(str(get_key()))
            lcd.set_cursor(i, 1)
            lcd.message(str(get_key()))
            time.sleep(0.5)

        lcd.clear()
        lcd.message("Please wait...")
        site = 'http://www.iotgecko.com/IOTHit.aspx?Id=dbaral29@gmail.com&Pass=4542&Data=' + str(user) + '*' + str(amount[0]) + str(amount[1]) + str(amount[2])
        getResponse = check_connectivity()
        if(getResponse.startswith('0') == True):
            lcd.clear()
            lcd.message("Sorry!! \nLow Balance")
            time.sleep(2)
            lcd.clear()
            lcd.message("Scan your Card:\n")
        else:
            samount = str(amount[0]) + str(amount[1]) + str(amount[2])
            iamount = int(samount)
            lcd.clear()
            lcd.message("Pump ON!\nAmount: " + str(amount[0]) + str(amount[1]) + str(amount[2]))
            
            if(iamount >= 0 and iamount < 100):
                GPIO.output(pump, False)
                time.sleep(3)
                GPIO.output(pump, True)
            elif(iamount >= 100 and iamount < 200):
                GPIO.output(pump, False)
                time.sleep(6)
                GPIO.output(pump, True)
            elif(iamount >= 200 and iamount < 300):
                GPIO.output(pump, False)
                time.sleep(9)
                GPIO.output(pump, True)
            elif(iamount >= 300 and iamount < 400):
                GPIO.output(pump, False)
                time.sleep(12)
                GPIO.output(pump, True)
            elif(iamount >= 400 and iamount < 500):
                GPIO.output(pump, False)
                time.sleep(15)
                GPIO.output(pump, True)
            elif(iamount >= 500 and iamount < 600):
                GPIO.output(pump, False)
                time.sleep(18)
                GPIO.output(pump, True)
            elif(iamount >= 700 and iamount < 800):
                GPIO.output(pump, False)
                time.sleep(21)
                GPIO.output(pump, True)
            elif(iamount >= 900 and iamount < 1000):
                GPIO.output(pump, False)
                time.sleep(23)
                GPIO.output(pump, True)

            if(getResponse == "/span"):
                lcd.clear()
                lcd.message("Sorry!! \nLow Balance")
                time.sleep(2)
                lcd.clear()
                lcd.message("Scan your Card:\n")
            else:
                text_word = getResponse.split('*')
                print(text_word)
                lcd.clear()
                lcd.message("Balance Amount:\n" + str(text_word[1]))
                time.sleep(3)

            amount = []

            lcd.clear()
            lcd.message("Scan your Card:\n")

        
        
        

    
