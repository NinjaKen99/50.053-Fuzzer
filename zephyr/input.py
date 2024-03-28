#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import json
import logging
import asyncio
import sys
import os
from binascii import hexlify
import time

from bumble.device import Device, Peer
from bumble.host import Host
from bumble.gatt import show_services
from bumble.core import ProtocolError
from bumble.controller import Controller
from bumble.link import LocalLink
from bumble.transport import open_transport_or_link, open_transport
from bumble.utils import AsyncRunner
from bumble.colors import color
import subprocess
from bumble.gatt_client import ServiceProxy, CharacteristicProxy, DescriptorProxy, UUID


async def write_target(target, attribute, bytes):
    # Write
    try:
        bytes_to_write = bytearray(bytes)
        await target.write_value(attribute, bytes_to_write, True)
        print(
            color(
                f"[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}",
                "green",
            )
        )
        return True
    except ProtocolError as error:
        print(
            color(f"[!]  Cannot write attribute 0x{attribute.handle:04X}:", "yellow"),
            error,
        )
    except TimeoutError:
        print(color("[X] Write Timeout", "red"))

    return False


async def read_target(target, attribute):
    # Read
    try:
        read = await target.read_value(attribute)
        value = read.decode("latin-1")
        print(
            color(
                f"[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}",
                "cyan",
            )
        )
        return value
    except ProtocolError as error:
        print(
            color(f"[!]  Cannot read attribute 0x{attribute.handle:04X}:", "yellow"),
            error,
        )
    except TimeoutError:
        print(color("[!] Read Timeout"))

    return None


# -----------------------------------------------------------------------------
class TargetServicesListener(Device.Listener):

    got_advertisement = False
    advertisement = None
    connection = None
    services = None
    transcation_done = False

    def on_advertisement(self, advertisement):

        print(
            f'{color("Advertisement", "cyan")} <-- '
            f'{color(advertisement.address, "yellow")}'
        )

        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        print(color(f"[OK] Connected!", "green"))
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        print("=== Discovering services")
        target = Peer(connection)
        attributes = dict()
        await target.discover_services()
        attributes["services"] = dict()
        for service in target.services:
            await service.discover_characteristics()
            attributes["services"][service.uuid.name] = {"object": service}
            try:
                value = await service.read_value()
                attributes["services"][service]["value"] = value
            except:
                pass
            attributes["services"][service.uuid.name]["characteristics"] = dict()
            for characteristic in service.characteristics:
                attributes["services"][service.uuid.name]["characteristics"][characteristic.uuid.name] = {
                    "descriptors": {},
                    "object": characteristic,
                    "permissions": characteristic.properties
                }
                try:
                    value = await characteristic.read_value()
                    attributes["services"][service.uuid.name]["characteristics"][characteristic.uuid.name][
                        "value"
                    ] = value
                except:
                    pass
                await characteristic.discover_descriptors()
                for descriptor in characteristic.descriptors:
                    try:
                        value = await descriptor.read_value()
                    except:
                        value = None
                        pass
                    attributes["services"][service.uuid.name]["characteristics"][characteristic.uuid.name][
                        "descriptors"
                    ][descriptor.type] = {"object": descriptor, "value": value}
                    
        print(color("[OK] Services discovered", "green"))
        self.services = attributes
        self.transcation_done = True
        return


# -----------------------------------------------------------------------------


class TargetSendListener(Device.Listener):

    got_advertisement = False
    advertisement = None
    connection = None
    transcation_done = False
    result = None
    status = None

    def __init__(self, attribute, payload) -> None:
        super().__init__()
        self.attribute = attribute
        self.payload = payload

    def on_advertisement(self, advertisement):

        print(
            f'{color("Advertisement", "cyan")} <-- '
            f'{color(advertisement.address, "yellow")}'
        )

        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        print(color(f"[OK] Connected!", "green"))
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        print("=== Discovering services")
        target = Peer(connection)

        self.status = await write_target(target, self.attribute, self.payload)
        self.result = await read_target(target, self.attribute)
        self.transcation_done = True
        return


class TargetEventsListener(Device.Listener):

    got_advertisement = False
    advertisement = None
    connection = None

    def __init__(self) -> None:
        super().__init__()
        self.transcation_done = False

    def on_advertisement(self, advertisement):

        print(
            f'{color("Advertisement", "cyan")} <-- '
            f'{color(advertisement.address, "yellow")}'
        )

        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        print(color(f"[OK] Connected!", "green"))
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        print("=== Discovering services")
        target = Peer(connection)
        attributes = []
        await target.discover_services()
        for service in target.services:
            attributes.append(service)
            await service.discover_characteristics()
            for characteristic in service.characteristics:
                attributes.append(characteristic)
                await characteristic.discover_descriptors()
                for descriptor in characteristic.descriptors:
                    attributes.append(descriptor)

        print(color("[OK] Services discovered", "green"))
        show_services(target.services)

        # -------- Main interaction with the target here --------
        print("=== Read/Write Attributes (Handles)")
        for attribute in attributes:
            await write_target(target, attribute, [0x01])
            await read_target(target, attribute)

        print("---------------------------------------------------------------")
        print(color("[OK] Communication Finished", "green"))
        print("---------------------------------------------------------------")
        self.transcation_done = True
        # ---------------------------------------------------


class BLEClient:

    def __init__(self, port):
        self.port = port
        self.hci_source = None
        self.hci_sink = None

    async def call_process(self, *args):
        process = subprocess.Popen(
            ["./zephyr.exe", "--bt-dev=127.0.0.1:" + str(self.port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd="targets/Zephyr",
        )
        return process

    async def initalize_transport(self):
        print(">>> Waiting connection to HCI...")
        async with await open_transport_or_link(
            "tcp-server:127.0.0.1" + ":" + str(self.port)
        ) as (hci_source, hci_sink):
            self.hci_source = hci_source
            self.hci_sink = hci_sink
            print(">>> Connected")
    # -----------------------------------------------------------------------------

    async def connection_basic(self, request, attribute=None, payload=None):

        # Create a local communication channel between multiple controllers
        link = LocalLink()

        # Create a first controller for connection with host interface (Zephyr)
        zephyr_controller = Controller(
            "Zephyr", host_source=self.hci_source, host_sink=self.hci_sink, link=link
        )

        # Create our own device (tester central) to manage the host BLE stack
        device = Device.from_config_file("./zephyr/tester_config.json")
        # Create a host for the second controller
        device.host = Host()
        # Create a second controller for connection with this test driver (Bumble)
        device.host.controller = Controller("Fuzzer", link=link)
        # Connect class to receive events during communication with target
        if request == "service":
            device.listener = TargetServicesListener()
        elif request == "send":
            device.listener = TargetSendListener(
                attribute=attribute, payload=payload
            )
        # Start BLE scanning here
        await device.power_on()
        await device.start_scanning()  # this calls "on_advertisement"

        print("Waiting Advertisment from BLE Target")
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning()  # Stop scanning for targets

        print(color("\n[OK] Got Advertisment from BLE Target!", "green"))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        print(f"=== Connecting to {target_address}...")
        await device.connect(target_address)  # this calls "on_connection"

        # Wait in an infinite loop
        while device.listener.transcation_done == False:
            await asyncio.sleep(0.5)

        if request == "service":
            return device.listener.services
        elif request == "send":
            return device.listener.result, device.listener.status
            

    async def get_services(self):
        process = await self.call_process()
        services = await self.connection_basic("service")
        process.terminate()
        await asyncio.sleep(3)
        return services

    async def send_payload(self, payload, service, characteristic):
        return await self.connection_basic("send", characteristic, payload)


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get("BUMBLE_LOGLEVEL", "INFO").upper())
#services = asyncio.run(BLEClient(9000).get_services())
# x: ServiceProxy
# for x in services["services"]:
#     print("Service")
#     print(x.uuid)  # UUID-16:xxxx (name) | 12345678-1234-5678-1234-56789ABCDEF0
#     print(
#         x.type
#     )  # Primary Serice | Generic Attribute | Generic Access | Battery | Current Time | Device Information | Heart Rate | Immediate Alert
#     try:
#         print(services["services"][x]["value"])
#     except:
#         pass
#     y: CharacteristicProxy
#     for y in services["services"][x]["characteristics"]:
#         print("     Characteristic")
#         print(
#             "     " + str(y.uuid)
#         )  # UUID-16:xxxx (name) | 12345678-1234-5678-1234-56789ABCDEF0
#         print(
#             "     " + str(y.properties)
#         )  # READ | WRITE | INDICATE | WRITE_NO_RESPONSE | NOTIFY | EXTENDED_PROPERTIES | AUTHENTICATED_SIGNED_WRITES
#         try:
#             print("     " + str(services["services"][x]["characteristics"][y]["value"]))
#         except:
#             pass
#         for z in services["services"][x]["characteristics"][y]["descriptors"]:
#             print("         Descriptor")
#             print("         " + str(z[0].type))
#             print("         " + str(z[1]))
            
#json.dump(services, open("services.json", "w"))

# for x in example:
#     print(x)
#     print(example[x])
