from setuptools import setup

setup(
    name='mqtt-zabbix-sender',
    version='0.1',
    scripts="mqtt_zabbix_sender",
    url='https://github.com/Depau/mqtt-zabbix-sender',
    license='GPL-3.0',
    author='Davide Depau',
    author_email='davide@depau.eu',
    description='Subscribe to MQTT events and send them to Zabbix for monitoring',
    install_requires=["pyjq", "pyyaml", "paho-mqtt", 'py-zabbix', 'six'],
    entry_points={
        "console_scripts": [
            "mqtt_zabbix_sender = mqtt_zabbix_sender:main"
        ]
    }
)
