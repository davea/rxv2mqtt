#!/usr/bin/env python
import os
import asyncio

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0

import rxv

RECEIVER_ADDR = os.environ.get('RECEIVER_ADDR')
RECEIVER_VOLUME = float(os.environ.get('RECEIVER_VOLUME', -60.0))

MQTT_TOPICS = os.environ['MQTT_TOPICS'].split(",")
MQTT_BROKER = os.environ['MQTT_BROKER']

rxv_client = None


async def mqtt_loop():
    topics = [(topic, QOS_0) for topic in MQTT_TOPICS]
    client = MQTTClient()
    await client.connect(MQTT_BROKER)
    await client.subscribe(topics)
    try:
        while True:
            message = await client.deliver_message()
            packet = message.publish_packet
            topic = packet.variable_header.topic_name
            payload = bytes(packet.payload.data)
            await handle_message(topic, payload)
        await client.unsubscribe(topics)
        await client.disconnect()
    except ClientException:
        raise


async def handle_message(topic: str, payload: bytes):
    if payload == b"off":
        print("Switching off")
        rxv_client.on = False
    else:
        station = payload.decode("utf-8")
        volume = min(RECEIVER_VOLUME, -45) # no loud surprises
        print(f"Playing {station} at {volume}dB")
        rxv_client.on = True
        rxv_client.net_radio(station)
        rxv_client.volume = volume


def setup_rxv():
    global rxv_client
    if RECEIVER_ADDR:
        ctrl_url = f"http://{RECEIVER_ADDR}:80/YamahaRemoteControl/ctrl"
        rxv_client = rxv.RXV(ctrl_url)
    else:
        rxv_client = rxv.find()[0]


async def main_loop():
    setup_rxv()
    await mqtt_loop()


def main():
    asyncio.get_event_loop().run_until_complete(main_loop())


if __name__ == '__main__':
    main()
