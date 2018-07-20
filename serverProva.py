import sys
import time
import psutil
from threading import Thread
from opcua import ua, Server
from math import sin
import threading

sys.path.insert(0, "..")


# COMPLETED: mettere il thread per l'aggiornamento delle variabili
# COMPLETED: mettere i lock sulle variabili
# TODO: esporre i GPIO del raspberry PI
# TODO: esporre metodo per far blinkare un LED
# COMPLETED: creare i certificati


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


if __name__ == "__main__":
    
    lock = threading.RLock()

    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    server.load_private_key("myPrivateKey.pem")
    server.load_certificate("myCertificate.der")

    server.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                                ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
                                ua.SecurityPolicyType.Basic128Rsa15_Sign])

    uri = "silvia-notebook.opcua.it/freeopcua/server"
    idx = server.register_namespace(uri)

    objects = server.get_objects_node()

    myobj = objects.add_object(idx, "MyObject")
    sinFunc = myobj.add_variable(idx, "MySin", 0, ua.VariantType.Float)

    core0temp = myobj.add_variable(idx, "Core0Temperature", 0)
    #core1temp = myobj.add_variable(idx, "Core1Temperature", psutil.sensors_temperatures()['coretemp'][2].current)
    core0temp.set_writable()
    #core1temp.set_writable()

    # starting!
    server.start()

    # TODO: avviare il Thread della funzione seno
    vup = SinUpdater(sinFunc)
    vup.start()
    
    try: #TODO: mettere questa pappardella in una funzione a parte che estende Thread (come il SinUpdater)
        while True:
            time.sleep(1)
            tFile = open('/sys/class/thermal/thermal_zone0/temp')
            temp = (float(tFile.read()))/1000
            #lockare
            with lock:
                core0temp.set_value(temp)
            #core1temp.set_value(psutil.sensors_temperatures()['coretemp'][2].current)
    finally:
        # close connection, remove subcsriptions, etc
        server.stop()
        tFile.close()
