import asyncio
from bleak import BleakScanner, BleakClient
import struct

ENV_SENSE_UUID = "0000181A-0000-1000-8000-00805f9b34fb"
ENV_SENSE_TEMP_UUID = "00002A6E-0000-1000-8000-00805f9b34fb"

temperature_data = None

def get_temperature():
    return temperature_data

def decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

async def find_temp_sensor():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name and "mpy-temp" in d.name:
            print(f"Scan: {d.name} {d.address}")
            return d.address
    return None

async def receive_temperature():
    global temperature_data
    while True:
        address = await find_temp_sensor()
        if not address:
            print("Sensor not found, retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue  # 見つからなければ再スキャン

        async with BleakClient(address) as client:
            if not client.is_connected:
                print("接続に失敗しました。再試行します。")
                continue

            print(f"Connected to {address}")
            while True:
                try:
                    data = await client.read_gatt_char(ENV_SENSE_TEMP_UUID)
                    temperature_data = decode_temperature(data)
                    await asyncio.sleep(5)
                except Exception as e:
                    print("読み取り中にエラーが発生:", e)
                    break  # 切断されたなどのケースで再スキャンに戻る