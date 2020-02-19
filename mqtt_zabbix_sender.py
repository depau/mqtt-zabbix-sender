import json
import logging
import sys

import paho.mqtt.client as mqtt
import pyjq
import yaml
from pyzabbix import ZabbixMetric, ZabbixSender


# noinspection PyShadowingNames
def read_config(path: str) -> dict:
    with open(path) as f:
        cfg = yaml.load(f, Loader=yaml.SafeLoader)

    # Pre-compile all JQ queries
    for topic, items in cfg["topics"].items():
        for item in items:
            if "jq" in item:
                item["jq"]["query"] = pyjq.compile(item["jq"]["query"])

    return cfg


# noinspection PyProtectedMember
def apply_jq(payload: str, jq: dict):
    if jq["ret"] not in ("first", "all"):
        raise ValueError("jq return value must be either 'first' or 'all'")

    # Dump JSON
    if jq.get("unmarshal", True):
        data = json.loads(payload)
    else:
        data = payload

    # Retrieve function (first/all)
    function = getattr(jq["query"], jq["ret"])

    # Apply to input
    result = function(j)

    # Convert result back to JSON
    if jq.get("marshal", True):
        return json.dumps(result)
    else:
        return result


# noinspection PyShadowingNames
class MQTTZabbixSender:
    def __init__(self, config: dict):
        self._cfg = config
        self._client = None

    def connect(self):
        self._client = mqtt.Client(client_id=self._cfg.get("client_id", ""))
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.connect(self._cfg["host"], self._cfg["port"], 60)
        logging.debug(f"Connected to broker {self._cfg['host']}")

    def loop_forever(self):
        self._client.loop_forever()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        for topic in self._cfg["topics"].keys():
            client.subscribe(topic, 1)
            logging.debug(f"Subscribed to {topic}")

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        if msg.topic not in self._cfg["topics"]:
            logging.warning(f"Ignoring unrequested topic: {msg.topic}")
            return
        else:
            items = self._cfg["topics"][msg.topic]

        metrics = []
        for item in items:
            payload = msg.payload

            if "jq" in item:
                payload = apply_jq(payload, item["jq"])

            metrics.append(ZabbixMetric(item["host"], item["item"], payload))

            logging.debug(f"{msg.topic} -> {item['item']}@{item['host']}{{{payload}}}")

        # noinspection PyTypeChecker
        result = ZabbixSender(use_config=True).send(metrics)


def main(args=tuple(sys.argv)):
    if len(args) < 2:
        raise SystemExit(f"Usage: {sys.argv[0]} [config]")

    cfg_path = args[1]
    cfg = read_config(cfg_path)

    log_level = getattr(logging, cfg.get("log_level", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=log_level)

    sender = MQTTZabbixSender(cfg)
    sender.connect()
    sender.loop_forever()


if __name__ == "__main__":
    main()
