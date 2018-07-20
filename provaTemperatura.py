while True:
  try:
    tFile = open('/sys/class/thermal/thermal_zone0/temp')
    temp = float(tFile.read())
    tempC = temp/1000
    print(tempC)

  except:
    tFile.close()
    GPIO.cleanup()
    exit