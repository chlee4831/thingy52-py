import asyncio
from bleak import *

# UUIDS
TCS_UUID              = 'ef6801009b3549339b1052ffa9740042'

TES_UUID              = 'ef6802009b3549339b1052ffa9740042'
TES_TEMP_UUID         = 'ef6802019b3549339b1052ffa9740042'
TES_PRESS_UUID        = 'ef6802029b3549339b1052ffa9740042'
TES_HUMID_UUID        = 'ef6802039b3549339b1052ffa9740042'
TES_GAS_UUID          = 'ef6802049b3549339b1052ffa9740042'
TES_COLOR_UUID        = 'ef6802059b3549339b1052ffa9740042'
TES_CONF_UUID         = 'ef6802069b3549339b1052ffa9740042'

UIS_UUID              = 'ef6803009b3549339b1052ffa9740042'
UIS_LED_UUID          = 'ef6803019b3549339b1052ffa9740042'
UIS_BTN_UUID          = 'ef6803029b3549339b1052ffa9740042'
UIS_PIN_UUID          = 'ef6803039b3549339b1052ffa9740042'

TMS_UUID              = 'ef6804009b3549339b1052ffa9740042'
TMS_CONF_UUID         = 'ef6804019b3549339b1052ffa9740042'
TMS_TAP_UUID          = 'ef6804029b3549339b1052ffa9740042'
TMS_ORIENTATION_UUID  = 'ef6804039b3549339b1052ffa9740042'
TMS_QUATERNION_UUID   = 'ef6804049b3549339b1052ffa9740042'
TMS_STEP_COUNTER_UUID = 'ef6804059b3549339b1052ffa9740042'
TMS_RAW_DATA_UUID     = 'ef6804069b3549339b1052ffa9740042'
TMS_EULER_UUID        = 'ef6804079b3549339b1052ffa9740042'
TMS_ROTATION_UUID     = 'ef6804089b3549339b1052ffa9740042'
TMS_HEADING_UUID      = 'ef6804099b3549339b1052ffa9740042'
TMS_GRAVITY_UUID      = 'ef68040a9b3549339b1052ffa9740042'

TSS_UUID              = 'ef6805009b3549339b1052ffa9740042'
TSS_CONF_UUID         = 'ef6805019b3549339b1052ffa9740042'
TSS_SPEAKER_DATA_UUID = 'ef6805029b3549339b1052ffa9740042'
TSS_SPEAKER_STAT_UUID = 'ef6805039b3549339b1052ffa9740042'
TSS_MIC_UUID          = 'ef6805049b3549339b1052ffa9740042'


async def scan():
    target_devices = []
    devices = await BleakScanner.discover()
    for dev in devices:
        if dev.name == 'Thingy':
            target_devices.append(dev)
    return target_devices

def notify_callback(sender, data):
    print(f"{sender}: {data}")

async def work(address):
    async with BleakClient(address) as client:

        services = await client.get_services()
        for service in services:
            print('service uuid:', service.uuid)
            for characteristic in service.characteristics:
                print('  uuid:', characteristic.uuid)
                print('  handle:', characteristic.handle) 
                print('  properties: ', characteristic.properties)
                if characteristic.uuid == TSS_MIC_UUID:  
                    if 'notify' in characteristic.properties:
                        print('try to activate notify.')
                        await client.start_notify(characteristic, notify_callback)
    
    while True:
        await asyncio.sleep(10.0)


async def main():
    scan_task = asyncio.create_task(scan())
    await scan_task
    target_devices = scan_task.result()
    print(target_devices)

    task_list = []
    for dev in target_devices:
        address = dev.address
        work_task = asyncio.create_task(work(address))
        task_list.append(work_task)
    
    while True:
        await asyncio.sleep(5.0)

if __name__ == "__main__":
    asyncio.run(main())