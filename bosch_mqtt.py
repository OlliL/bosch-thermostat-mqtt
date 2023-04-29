from typing import Any
import time
import os
import click
import logging
from colorlog import ColoredFormatter
import aiohttp
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const import XMPP, HTTP
from bosch_thermostat_client.const.ivt import IVT
from bosch_thermostat_client.const.nefit import NEFIT
from bosch_thermostat_client.const.easycontrol import EASYCONTROL
from bosch_thermostat_client.version import __version__
import json
import asyncio
from functools import wraps
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
import paho.mqtt.client as mqtt


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
fmt = "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
colorfmt = f"%(log_color)s{fmt}%(reset)s"
logging.getLogger().handlers[0].setFormatter(
    ColoredFormatter(
        colorfmt,
        datefmt=datefmt,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        },
    )
)

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        _LOGGER.error("MQTT Connection returned with result code "+str(rc))
    pass

def set_default(ctx, param, value):
    if os.path.exists(value):
        with open(value, 'r') as f:
            config = load(f.read(), Loader=Loader)
        ctx.default_map = config
    return value

def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options

def mqtt_connect():
    c = click.get_current_context()
    mqtt_host = c.params["mqtt_host"]
    mqtt_port = c.params["mqtt_port"]
    mqtt_username = c.params["mqtt_username"]
    mqtt_password = c.params["mqtt_password"]

    client = mqtt.Client(client_id="bosch-thermostat-mqtt")
    if mqtt_username is not None and mqtt_password is not None:
        client.username_pw_set(mqtt_username, mqtt_password)
    client.on_connect = on_connect

    client.connect(host=mqtt_host, port=mqtt_port)

    started = time.time()
    while time.time() - started < 5.0:
        client.loop()
        if client.is_connected():
            _LOGGER.info("Successfully connected to MQTT broker.")
            return client

    raise OSError('Connection to MQTT broker failed!')


def mqtt_publish(gateway, result):
    client = mqtt_connect()

    for res in result:
        if type(res) == list:
            for r in res:
                if 'value' in r:
                    topic = "bosch/" + gateway.device_model + "-" + gateway.uuid + r.get("id")
                    _LOGGER.info("Publishing %s", topic)
                    client.publish(topic=topic, payload=r.get("value"))

    client.disconnect()


async def _scan(gateway, smallscan):
    if smallscan:
        result = await gateway.smallscan(_type=smallscan.lower())
    else:
        result = await gateway.rawscan()

    mqtt_publish(gateway, result)

async def _runquery(gateway, path):
    result = []
    for p in path:
        result.append(await gateway.raw_query(p))

    mqtt_publish(gateway, [result])

async def _execute(gateway, fun):
    c = click.get_current_context()
    daemon = c.params["daemon"]
    interval = c.params["interval"]

    _LOGGER.debug("Trying to connect to gateway.")
    connected = await gateway.check_connection()
    if connected:
        _LOGGER.info("Successfully connected to gateway. Found UUID: %s", gateway.uuid)
        if daemon:
            _LOGGER.info("Executing as daemon, interval is %d seconds.", interval)
            while True:
                await fun()
                _LOGGER.info("Sleeping %d seconds...", interval)
                time.sleep(interval)
        else:
            await fun()
    else:
        _LOGGER.error("Couldn't connect to gateway!")

def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group(no_args_is_help=True)
@click.pass_context
@click.version_option(__version__)
@coro
async def cli(ctx):
    """A tool to run commands against Bosch thermostat."""

    pass


_cmd1_options = [
    click.option(
        "--config",
        default="config.yml",
        type=click.Path(),
        callback=set_default,
        is_eager=True,
        expose_value=False,
        show_default=True,
        help="Read configuration from PATH.",
    ),
    click.option(
        "--host",
        envvar="BOSCH_HOST",
        type=str,
        required=True,
        help="IP address of gateway or SERIAL for XMPP",
    ),
    click.option(
        "--token",
        envvar="BOSCH_ACCESS_TOKEN",
        type=str,
        required=True,
        help="Token from sticker without dashes.",
    ),
    click.option(
        "--password",
        envvar="BOSCH_PASSWORD",
        type=str,
        required=False,
        help="Password you set in mobile app.",
    ),
    click.option(
        "--protocol",
        envvar="BOSCH_PROTOCOL",
        type=click.Choice([XMPP, HTTP], case_sensitive=True),
        required=True,
        help="Bosch protocol. Either XMPP or HTTP.",
    ),
    click.option(
        "--device",
        envvar="BOSCH_DEVICE",
        type=click.Choice([NEFIT, IVT, EASYCONTROL], case_sensitive=False),
        required=True,
        help="Bosch device type. NEFIT, IVT or EASYCONTROL.",
    ),
    click.option(
        "-d",
        "--debug",
        default=False,
        count=True,
        help="Set Debug mode. Single debug is debug of this lib. Second d is debug of aioxmpp as well.",
    ),
]

_scan_options = [
    click.option(
        "-s",
        "--smallscan",
        type=click.Choice(["HC", "DHW", "SENSORS", "RECORDINGS"], case_sensitive=False),
        help="Scan only single circuit of thermostat.",
    ),
]

_mqtt_options = [
    click.option(
        "--daemon",
        is_flag=True,
        required=False,
        default=False,
        help="Start as daemon.",
    ),
    click.option(
        "--interval",
        default="300",
        type=int,
        show_default=True,
        help="Specify polling interval in seconds when started as daemon.",
    ),
    click.option(
        "--mqtt-host",
        type=str,
        required=True,
        help="Adress of MQTT host.",
    ),
    click.option(
        "--mqtt-port",
        default="1883",
        type=int,
        show_default=True,
        help="Port of MQTT host.",
    ),
    click.option(
        "--mqtt-username",
        type=str,
        required=False,
        help="Username for MQTT connect.",
    ),
    click.option(
        "--mqtt-password",
        type=str,
        required=False,
        help="Password for MQTT connect.",
    ),
]


@cli.command()
@add_options(_cmd1_options)
@add_options(_scan_options)
@add_options(_mqtt_options)
@click.pass_context
@coro
async def scan(
    ctx,
    host: str,
    token: str,
    password: str,
    protocol: str,
    device: str,
    debug: int,
    smallscan: str,
    mqtt_host: str,
    mqtt_port: int,
    mqtt_username: str,
    mqtt_password: str,
    daemon: bool,
    interval: int,
):
    """Create rawscan of Bosch thermostat."""
    if debug == 0:
        logging.basicConfig(level=logging.INFO)
    if debug > 0:
        logging.basicConfig(
            # colorfmt,
            datefmt=datefmt,
            level=logging.DEBUG,
            filename="out.log",
            filemode="a",
        )
        _LOGGER.info("Debug mode active")
        _LOGGER.debug(f"Lib version is {bosch.version}")
    if debug > 1:
        logging.getLogger("aioxmpp").setLevel(logging.DEBUG)
        logging.getLogger("aioopenssl").setLevel(logging.DEBUG)
        logging.getLogger("aiosasl").setLevel(logging.DEBUG)
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
    else:
        logging.getLogger("aioxmpp").setLevel(logging.WARN)
        logging.getLogger("aioopenssl").setLevel(logging.WARN)
        logging.getLogger("aiosasl").setLevel(logging.WARN)
        logging.getLogger("asyncio").setLevel(logging.WARN)

    if device.upper() in (NEFIT, IVT, EASYCONTROL):
        BoschGateway = bosch.gateway_chooser(device_type=device)
    else:
        _LOGGER.error("Wrong device type.")
        return
    session_type = protocol.upper()
    if session_type == XMPP:
        session = asyncio.get_event_loop()
    elif session_type == HTTP:
        session = aiohttp.ClientSession()
        if device.upper() != IVT:
            _LOGGER.warn(
                "You're using HTTP protocol, but your device probably doesn't support it. Check for mistakes!"
            )
    else:
        _LOGGER.error("Wrong protocol for this device")
        return
    try:
        gateway = BoschGateway(
            session=session,
            session_type=session_type,
            host=host,
            access_token=token,
            password=password,
        )

        await _execute(gateway, lambda: _scan(gateway, smallscan))
    finally:
        await gateway.close(force=True)


_path_options = [
    click.option(
        "-p",
        "--path",
        type=str,
        required=True,
        multiple=True,
        help="Path to run against. Look at rawscan at possible paths. e.g. /gateway/uuid - Can be specified multiple times!",
    )
]


@cli.command()
@add_options(_cmd1_options)
@add_options(_path_options)
@add_options(_mqtt_options)
@click.pass_context
@coro
async def query(
    ctx,
    host: str,
    token: str,
    password: str,
    protocol: str,
    device: str,
    path: list[str],
    debug: int,
    mqtt_host: str,
    mqtt_port: int,
    mqtt_username: str,
    mqtt_password: str,
    daemon: bool,
    interval: int,
):
    """Query values of Bosch thermostat."""
    if debug == 0:
        logging.basicConfig(level=logging.INFO)
    if debug > 0:
        _LOGGER.info("Debug mode active")
        _LOGGER.debug(f"Lib version is {bosch.version}")
    if debug > 1:
        logging.getLogger("aioxmpp").setLevel(logging.DEBUG)
        logging.getLogger("aioopenssl").setLevel(logging.DEBUG)
        logging.getLogger("aiosasl").setLevel(logging.DEBUG)
        logging.getLogger("asyncio").setLevel(logging.DEBUG)
    else:
        logging.getLogger("aioxmpp").setLevel(logging.WARN)
        logging.getLogger("aioopenssl").setLevel(logging.WARN)
        logging.getLogger("aiosasl").setLevel(logging.WARN)
        logging.getLogger("asyncio").setLevel(logging.WARN)
    if device.upper() in (NEFIT, IVT, EASYCONTROL):
        BoschGateway = bosch.gateway_chooser(device_type=device)
    else:
        _LOGGER.error("Wrong device type.")
        return
    session_type = protocol.upper()
    _LOGGER.info("Connecting to %s with '%s'", host, session_type)
    if session_type == XMPP:
        session = asyncio.get_event_loop()
    elif session_type == HTTP:
        session = aiohttp.ClientSession()
        if device.upper() != IVT:
            _LOGGER.warn(
                "You're using HTTP protocol, but your device probably doesn't support it. Check for mistakes!"
            )
    else:
        _LOGGER.error("Wrong protocol for this device")
        return
    try:
        gateway = BoschGateway(
            session=session,
            session_type=session_type,
            host=host,
            access_token=token,
            password=password,
        )

        await _execute(gateway, lambda: _runquery(gateway, path))
    finally:
        await gateway.close(force=True)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(cli())
