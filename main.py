#!/usr/bin/env python
import os

import rxv

from mqttwrapper import run_script

RECEIVER_ADDR = os.environ.get('RECEIVER_ADDR')
RECEIVER_VOLUME = float(os.environ.get('RECEIVER_VOLUME', -60.0))


def message_callback(topic: str, payload: bytes, rxv_client: rxv.RXV):
    if payload == b"off":
        # Don't switch off if another source is selected.
        if rxv_client.input == 'NET RADIO':
            print("Switching off")
            rxv_client.on = False
    else:
        station = payload.decode("utf-8")
        volume = min(RECEIVER_VOLUME, -45.0) # no loud surprises
        print(f"Playing {station} at {volume}dB")
        rxv_client.on = True
        rxv_client.net_radio(station)
        rxv_client.volume = volume


def setup_rxv():
    if RECEIVER_ADDR:
        ctrl_url = f"http://{RECEIVER_ADDR}:80/YamahaRemoteControl/ctrl"
        return rxv.RXV(ctrl_url)
    else:
        return rxv.find()[0]


def main():
    rxv_client = setup_rxv()
    run_script(message_callback, rxv_client=rxv_client)


if __name__ == '__main__':
    main()
