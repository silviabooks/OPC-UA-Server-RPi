import sys
import time
import psutil
from opcua import ua, Server
sys.path.insert(0, "..")

# TODO: mettere il thread per l'aggiornamento delle variabili
# TODO: mettere i lock sulle variabili
# TODO: esporre i GPIO del raspberry PI
# TODO: esporre metodo per far blinkare un LED
# TODO: creare i certificati

if __name__ == "__main__":
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.load_certificate("myCertificate.der")
    server.load_private_key("myPrivateKey.pem")
    server.set_security_policy([
        ua.SecurityPolicyType.NoSecurity,
        ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
        ua.SecurityPolicyType.Basic128Rsa15_Sign])

    uri = "silvia-notebook.opcua.it/freeopcua/server"
    idx = server.register_namespace(uri)

    objects = server.get_objects_node()

    myobj = objects.add_object(idx, "MyObject")
    core0temp = myobj.add_variable(idx, "Core0Temperature", psutil.sensors_temperatures()['coretemp'][1].current)
    core1temp = myobj.add_variable(idx, "Core1Temperature", psutil.sensors_temperatures()['coretemp'][2].current)
    core0temp.set_writable()
    core1temp.set_writable()

    # starting!
    server.start()
    
    try:
        while True:
            time.sleep(1)
            core0temp.set_value(psutil.sensors_temperatures()['coretemp'][1].current)
            core1temp.set_value(psutil.sensors_temperatures()['coretemp'][2].current)
    finally:
        # close connection, remove subcsriptions, etc
        server.stop()

