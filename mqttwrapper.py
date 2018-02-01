import asyncio

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0

async def mqtt_loop(broker, topics, callback, **kwargs):
    client = MQTTClient()
    await client.connect(broker)
    await client.subscribe([(topic, QOS_0) for topic in topics])
    try:
        while True:
            message = await client.deliver_message()
            packet = message.publish_packet
            topic = packet.variable_header.topic_name
            payload = bytes(packet.payload.data)
            callback(topic, payload, **kwargs)
        await client.unsubscribe(topics)
        await client.disconnect()
    except ClientException:
        raise


def run_script(broker, topics, callback, **kwargs):
    asyncio.get_event_loop().run_until_complete(mqtt_loop(broker, topics, callback, **kwargs))
