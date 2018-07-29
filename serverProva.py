import sys
import time
# import psutil
from threading import Thread
from opcua import ua, uamethod, Server
from math import sin
import threading
import RPi.GPIO as GPIO

# sys.path.insert(0, "..")


# COMPLETED: mettere il thread per l'aggiornamento delle variabili
# COMPLETED: mettere i lock sulle variabili
# TODO: esporre i GPIO del raspberry PI
# TODO: esporre metodo per far blinkare un LED
# COMPLETED: creare i certificati

@uamethod
def BlinkLed(parent, numTimes, speed):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    for i in range(0,numTimes):
        GPIO.output(7,True) # Switch on pin 7
        time.sleep(speed)
        GPIO.output(7,False) # Switch off pin 7
        time.sleep(speed)
    GPIO.cleanup()
    return


class SinUpdater(Thread):
    def __init__(self, var):
        Thread.__init__(self)
        self._stop = False
        self.var = var

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            v = sin(time.time() / 10)
            self.var.set_value(v)
            time.sleep(0.1)


class CoreUpdater(Thread):
    def __init__(self, var):
        Thread.__init__(self)
        self._stop = False
        self.var = var

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            time.sleep(1)
            tFile = open('/sys/class/thermal/thermal_zone0/temp')
            temp = (float(tFile.read())) / 1000
            # lockare
            with lock:
                self.var.set_value(temp)
            tFile.close()


# if __name__ == "__main__":
    
lock = threading.RLock()

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

# Load private key
#server.load_private_key("myPrivateKey.pem")
# Load public key
#server.load_certificate("myCertificate.der")

server.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                            ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
                            ua.SecurityPolicyType.Basic128Rsa15_Sign]) #Security level of server

uri = "silvia-notebook.opcua.it/freeopcua/server"
idx = server.register_namespace(uri)

objects = server.get_objects_node()

myObj = objects.add_object(idx, "MyObject")
sinFunc = myObj.add_variable(idx, "MySin", 0, ua.VariantType.Float)
core0temp = myObj.add_variable(idx, "Core0Temperature", 0)
myObj.add_method(idx, "BlinkLed", BlinkLed, [ua.VariantType.Int64, ua.VariantType.Int64], [])

# core1temp = myObj.add_variable(idx, "Core1Temperature", psutil.sensors_temperatures()['coretemp'][2].current)
core0temp.set_writable()
varToSet.set_writable()
# core1temp.set_writable()

# starting!
server.start()

# COMPLETED: avviare il Thread della funzione seno
sinUp = SinUpdater(sinFunc)
sinUp.start()
coreUp = CoreUpdater(core0temp)
coreUp.start()

input("Press Enter to stop the server")

sinUp.stop()
coreUp.stop()
server.stop()

"""try: #COMPLETED: mettere questa pappardella in una funzione a parte che estende Thread (come il SinUpdater)
    while True:
        time.sleep(1)
        tFile = open('/sys/class/thermal/thermal_zone0/temp')
        temp = (float(tFile.read()))/1000
        #lockare
        with lock:
            core0temp.set_value(temp)
        #core1temp.set_value(psutil.sensors_temperatures()['coretemp'][2].current)
finally:
    # close connection, remove subcsriptions, etc"""
