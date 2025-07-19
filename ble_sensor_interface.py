import asyncio
from bleak import BleakScanner, BleakClient
import struct

ENV_SENSE_TEMP_UUID = "00002A6E-0000-1000-8000-00805f9b34fb"

class BleSensorInterface:
    def __init__(self):
        self.client = None
        self.connected = False
        self.temperature = None
        self.loop = None  # Flask側で代入

    def set_loop(self, loop):
        self.loop = loop

    async def connect(self):
        devices = await BleakScanner.discover()
        for device in devices:
            if device.name and "mpy-temp" in device.name:
                self.client = BleakClient(device.address)
                await self.client.connect()
                self.connected = True
                print(f"Connected to {device.name}")
                return True
        print("Device not found")
        return False

    async def read_loop(self):
        if not self.connected:
            success = await self.connect()
            if not success:
                return

        try:
            while self.connected:
                raw = await self.client.read_gatt_char(ENV_SENSE_TEMP_UUID)
                self.temperature = struct.unpack("<h", raw)[0] / 100
                print(f"温度: {self.temperature:.2f} °C")
                await asyncio.sleep(5)
        except Exception as e:
            print("読み取りエラー:", e)
        finally:
            await self.disconnect()

    async def disconnect(self):
        if self.client and self.connected:
            self.connected = False  # 先に切断状態に
            await self.client.disconnect()
            self.client = None
            print("切断しました")