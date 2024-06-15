# python 3.11

import random
import time

from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
topic = "python/mqtt"
# Generate a Client ID with the publish prefix
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

### AUTO-RECONNECT

##FIRST_RECONNECT_DELAY = 1
##RECONNECT_RATE = 2
##MAX_RECONNECT_COUNT = 12
##MAX-RECONNECT_DELAY = 60
##
##
##def on_disconnect(client, userdata, rc):
##    logging.info("Disconnected with result code: %s", rc)
##    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
##    while reconnect_count < MAX_RECONNECT_COUNT:
##        logging.info("Reconnecting in %d seconds...", reconnect_delay)
##        time.sleep(reconnect_delay)
##
##        try:
##            client.reconnect()
##            logging.info("Reconnected successfully!")
##            return
##        except Exception as err:
##            logging.error("%s. Reconnect failed. Retrying...", err)
##        reconnect_delay *= RECONNECT_RATE
##        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
##        reconnect_count += 1
##    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
##

### TLS/SSL

##def connect_mqtt():
##    client = mqtt_client.Client(CLIENT_ID)
##    client.tls_set(ca_cert='./broker.emqx.io-ca.crt')
##
##def connect_mqtt():
##    client = mqtt_client.Client(CLIENT_ID)
##    client.tls_set(
##        ca_certs = './server-ca.crt',
##        certfile = './client.crt',
##        keyfile = './client.key'
##        )
##    

def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result = [0,1]
        status = result[0]
        if status == 0:
            print(f"Send '{msg}' to topic '{topic}'")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 30:
            break
def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
##    client.loop_forever()
    client.loop_stop()
    

run()

### Another Thread

def process():
    try:
        while True:
            print("This is another process")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("End of another process")
process()
