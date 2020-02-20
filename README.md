# MQTT Zabbix Sender

Send data from MQTT to Zabbix items for monitoring.

- Supports unauthenticated MQTT broker
  - Authentication can be added but I don't need it. Send a PR and I'll accept it ;)
- Supports sending an MQTT topic to multiple items
- Supports applying [./jq](https://stedolan.github.io/jq/) transformations to JSON
  payloads

## Usage

Install it with `pip install .`, or install the requirements with
`pip install -r requirements.txt`.

Then either run `mqtt_zabbix_sender` from `$PATH` or `./mqtt_zabbix_sender.py`
from this directory.

The only required option is the path to a YAML configuration file. You can find
an example in the repo.

## Set up Zabbix items

- Go to **Configuration** > **Hosts** > (your host) > **Items**.
- Click **Create item** on the upper right
  - Name: a name of your choice
  - Type: **Zabbix trapper** (yo)
  - Key: key of your choice (it has to be the same in the config file)
  - Create or select an application type for easier data retrieval in the UI,
    like "Smart home service" and "Smart home device".

## Configure topics

`topics` in the config YAML must be a mapping `topic`:`[items]`.

Each topic can be sent to multiple Zabbix items (metrics). That can be useful to
provide multiple representations of the same data or, combined with `jq` queries,
to split and handle JSON payloads containing multiple metrics.

For example, when a button on an IKEA TRADFRI remote is pressed,
[Zigbee2MQTT](https://www.zigbee2mqtt.io/) sends a JSON payload like the
following:

```json
{"battery": 100, "linkquality": 100, "action": "toggle"}
```

We can extract both the battery level and the link quality into their own
separate metrics:

```yaml
  'zigbee2mqtt/tradfri_remote':
    - host: rock64
      item: zigbee2mqtt.tradfri_remote.battery
      jq:
        query: '.battery'
        return: first
    - host: rock64
      item: zigbee2mqtt.tradfri_remote.linkquality
      jq:
        query: '.linkquality'
        return: first
```

Zigbee2MQTT also reports its service status, which can be useful too. It's
reported as either `online` or `offline`. A jq query can help with that too:

```yaml
  'zigbee2mqtt/bridge/state':
    # Send the state as-is
    - host: rock64
      item: zigbee2mqtt.bridge.state

    # Also send it as an integer, useful for graphing
    - host: rock64
      item: zigbee2mqtt.bridge.online
      jq:
        unmarshal: false
        marshal: true
        return: first
        query: 'if . == "online" then 1 else 0 end'
```

### `jq` item allowed fields

- `return`: must be either `first` or `all`. `first` returns the first
  result, `all` returns all of them as a list.
- `query`: the JQ query
- `unmarshal`: whether the input payload should be parsed as a JSON object
  before applying JQ. If `false`, the payload will be treated as a JSON
  string. Default is `true`.
- `marshal`: whether the JQ output must be converted back to a JSON-formatted
  string or not. If `false` you must ensure the result is a string. Set to
  false always when the JQ result is already a string and can be sent directly
  to Zabbix. Default is `true`.


See the [sample config](config.example.yml) for a full example.
