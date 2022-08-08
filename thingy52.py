import asyncio
from bleak import *
import soundfile as sf

# UUIDS
TCS_UUID              = 'ef680100-9b35-4933-9b10-52ffa9740042'

TES_UUID              = 'ef680200-9b35-4933-9b10-52ffa9740042'
TES_TEMP_UUID         = 'ef680201-9b35-4933-9b10-52ffa9740042'
TES_PRESS_UUID        = 'ef680202-9b35-4933-9b10-52ffa9740042'
TES_HUMID_UUID        = 'ef680203-9b35-4933-9b10-52ffa9740042'
TES_GAS_UUID          = 'ef680204-9b35-4933-9b10-52ffa9740042'
TES_COLOR_UUID        = 'ef680205-9b35-4933-9b10-52ffa9740042'
TES_CONF_UUID         = 'ef680206-9b35-4933-9b10-52ffa9740042'

UIS_UUID              = 'ef680300-9b35-4933-9b10-52ffa9740042'
UIS_LED_UUID          = 'ef680301-9b35-4933-9b10-52ffa9740042'
UIS_BTN_UUID          = 'ef680302-9b35-4933-9b10-52ffa9740042'
UIS_PIN_UUID          = 'ef680303-9b35-4933-9b10-52ffa9740042'

TMS_UUID              = 'ef680400-9b35-4933-9b10-52ffa9740042'
TMS_CONF_UUID         = 'ef680401-9b35-4933-9b10-52ffa9740042'
TMS_TAP_UUID          = 'ef680402-9b35-4933-9b10-52ffa9740042'
TMS_ORIENTATION_UUID  = 'ef680403-9b35-4933-9b10-52ffa9740042'
TMS_QUATERNION_UUID   = 'ef680404-9b35-4933-9b10-52ffa9740042'
TMS_STEP_COUNTER_UUID = 'ef680405-9b35-4933-9b10-52ffa9740042'
TMS_RAW_DATA_UUID     = 'ef680406-9b35-4933-9b10-52ffa9740042'
TMS_EULER_UUID        = 'ef680407-9b35-4933-9b10-52ffa9740042'
TMS_ROTATION_UUID     = 'ef680408-9b35-4933-9b10-52ffa9740042'
TMS_HEADING_UUID      = 'ef680409-9b35-4933-9b10-52ffa9740042'
TMS_GRAVITY_UUID      = 'ef68040a-9b35-4933-9b10-52ffa9740042'

TSS_UUID              = 'ef680500-9b35-4933-9b10-52ffa9740042'
TSS_CONF_UUID         = 'ef680501-9b35-4933-9b10-52ffa9740042'
TSS_SPEAKER_DATA_UUID = 'ef680502-9b35-4933-9b10-52ffa9740042'
TSS_SPEAKER_STAT_UUID = 'ef680503-9b35-4933-9b10-52ffa9740042'
TSS_MIC_UUID          = 'ef680504-9b35-4933-9b10-52ffa9740042'

# /** Intel ADPCM step variation table */
INDEX_TABLE = [-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8,]

# /** ADPCM step size table */
STEP_SIZE_TABLE = [7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143, 157, 173, 190, 209,
                   230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358,
                   5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767]

pcm_buffer = []

def adpcm_decode(adpcm) :
    # // Allocate output buffer
    pcm = []

    # // The first 2 bytes of ADPCM frame are the predicted value
    valuePredicted = int.from_bytes(adpcm[:2], byteorder='big', signed=True)
	# // The 3rd byte is the index value
    index = int(adpcm[2])
    data = adpcm[3:]

    if (index < 0) :
        index = 0
    if (index > 88) :
        index = 88

    for value in data :
        deltas = [(value >> 4) & 0x0f, value & 0x0f]
        for delta in deltas :
            # Update step value
            step = STEP_SIZE_TABLE[index]
            
            # /* Step 2 - Find new index value (for later) */
            index = index + INDEX_TABLE[delta]
            if index < 0 :
                index = 0
            if index > 88 :
                index = 88

            # /* Step 3 - Separate sign and magnitude */
            sign = delta & 8
            delta = delta & 7

            # /* Step 4 - Compute difference and new predicted value */
            diff = (step >> 3)
            if (delta & 4) > 0 :
                diff += step
            if (delta & 2) > 0 :
                diff += step >> 1
            if (delta & 1) > 0 :
                diff += step >> 2

            if sign > 0 :
                valuePredicted = valuePredicted-diff
            else :
                valuePredicted = valuePredicted+diff

            # /* Step 5 - clamp output value */
            if valuePredicted > 32767 :
                valuePredicted = 32767
            elif valuePredicted < -32768 :
                valuePredicted = -32768

            valuePredicted = valuePredicted/32768
            # /* Step 7 - Output value */
            pcm.append(valuePredicted)

    return pcm

async def scan():
    target_devices = []
    devices = await BleakScanner.discover()
    for dev in devices:
        if dev.name == 'Thingy':
            target_devices.append(dev)
    return target_devices

def notify_callback(sender, data):
    pcm = adpcm_decode(data)

    pcm_buffer.extend(pcm)
    if(len(pcm_buffer) > 160000) :
        print(pcm_buffer[:160000])
        sf.write("test.wav", pcm_buffer, 16000, subtype='PCM_16')
        pcm_buffer.clear()
    
    # print(f"{sender}, {len(pcm)}: {pcm}")

def disconnected_callback(client):
    print(f'Device {client.address} disconnected')

async def work(address):
    async with BleakClient(address) as client:
        client.set_disconnected_callback(disconnected_callback)

        services = await client.get_services()
        # for service in services:
        #     print('service uuid:', service.uuid)
        #     for characteristic in service.characteristics:
        #         print('  uuid:', characteristic.uuid)
        #         print('  handle:', characteristic.handle) 
        #         print('  properties: ', characteristic.properties)
        #         if characteristic.uuid == TSS_MIC_UUID:  
        #             if 'notify' in characteristic.properties:
        #                 print('try to activate notify.')
        #                 await client.start_notify(characteristic, notify_callback)
        await client.start_notify(TSS_MIC_UUID, notify_callback)
    
        while client.is_connected :            
            await asyncio.sleep(5.0)
    
    print(f'Work task for {address} end')


async def main():
    target_devices = await scan()
    print(target_devices)

    task_list = []
    for dev in target_devices:
        address = dev.address
        work_task = asyncio.create_task(work(address))
        task_list.append(work_task)
    
    for task in task_list :
        await task    
    
    print("Main task end")

if __name__ == "__main__":
    asyncio.run(main())