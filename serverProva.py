import time
import dht11
from threading import Thread
from opcua import ua, uamethod, Server
from math import sin
import threading
import RPi.GPIO as GPIO


@uamethod
def BlinkLed(parent, numTimes, speed):
    blinkLed = Blink(numTimes, speed)
    blinkLed.start()
    return


class Blink(Thread):
    def __init__(self, numTimes, speed):
        Thread.__init__(self)
        self._stop = False
        self.numTimes = numTimes
        self.speed = speed

    def stop(self):
        self._stop = True

    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(7, GPIO.OUT)
        for i in range(0, self.numTimes):
            # Switch on pin 7
            GPIO.output(7, True)
            time.sleep(self.speed)
            # Switch off pin 7
            GPIO.output(7, False)
            time.sleep(self.speed)
        GPIO.cleanup()
        self.stop()


@uamethod
def ReadHumidityTemperature(parent):
    vector = []
    with lock:
        vector[0] = sensorTemp.get_value()
        vector[1] = sensorHum.get_value()
    return vector[0], vector[1]


class SensorUpdater(Thread):
    def __init__(self, temp, hum):
        Thread.__init__(self)
        self._stop = False
        self.temp = temp
        self.hum = hum

    def stop(self):
        self._stop = True

    def run(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        instance = dht11.DHT11(pin=18)
        while not self._stop:
            result = instance.read()
            with lock:
                if result.is_valid():
                    self.temp.set_value(result.temperature)
                    self.hum.set_value(result.humidity)
                else:
                    self.temp.set_value(0)
                    self.hum.set_value(0)
            time.sleep(0.5)


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
            with lock:
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
            # Lock to set the variable
            with lock:
                self.var.set_value(temp)
            tFile.close()


lock = threading.RLock()

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

# Load private key
server.load_private_key("myPrivateKey.pem")
# Load public key
server.load_certificate("myCertificate.der")

# Security level of server
server.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
                ua.SecurityPolicyType.Basic128Rsa15_Sign,
                ua.SecurityPolicyType.Basic256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256_Sign])

uri = "silvia-notebook.opcua.it/freeopcua/server"
idx = server.register_namespace(uri)

objects = server.get_objects_node()

myObj = objects.add_object(idx, "RaspberryPi")
sinFunc = myObj.add_variable(idx, "SinExample", 0, ua.VariantType.Float)
core0temp = myObj.add_variable(idx, "Core0Temperature", 0)
sensorTemp = myObj.add_variable(idx, "SensorTemperature", 0)
sensorHum = myObj.add_variable(idx, "SensorHumidity", 0)
myObj.add_method(idx, "BlinkLed", BlinkLed, [ua.VariantType.Int64, ua.VariantType.Int64], [])

temp = ua.Argument()
temp.Name = "Temperature"
temp.DataType = ua.NodeId(ua.ObjectIds.Int64)
temp.ValueRank = -1
temp.ArrayDimensions = []
temp.Description = ua.LocalizedText("Output of sensor")
hum = ua.Argument()
hum.Name = "Humidity"
hum.DataType = ua.NodeId(ua.ObjectIds.Int64)
hum.ValueRank = -1
hum.ArrayDimensions = []
hum.Description = ua.LocalizedText("Output of sensor")

myObj.add_method(idx, "ReadHumidityTemperature", ReadHumidityTemperature, [], [temp, hum])

core0temp.set_writable()
sensorTemp.set_writable()
sensorHum.set_writable()

# Start Server
server.start()

sinUp = SinUpdater(sinFunc)
sinUp.start()
coreUp = CoreUpdater(core0temp)
coreUp.start()
sensorUp = SensorUpdater(sensorTemp, sensorHum)
sensorUp.start()

input("Press Enter to stop the server")

sinUp.stop()
coreUp.stop()
sensorUp.stop()
server.stop()
