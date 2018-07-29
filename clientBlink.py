from opcua import Client


if __name__ == "__main__":

    client = Client("opc.tcp://169.254.121.18:4840/freeopcua/server/")
    try:
        client.connect()
        client.load_type_definitions()

        root = client.get_root_node()

        obj = root.get_child(["0:Objects", "2:MyObject"])

        obj.call_method("2:BlinkLed", 1, 1)

    finally:
        client.disconnect()
