import asyncio
import queue

import numpy as np
import sounddevice as sd


async def stream_generator(sample_rate=44100, buffer_size=256, dtype='float32', channels=1, **kwargs):
    q_in = asyncio.Queue()
    q_out = queue.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, outdata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))
        try:
            outdata[:] = q_out.get_nowait()
        except queue.Empty:
            pass

    stream = sd.Stream(samplerate=sample_rate, blocksize=buffer_size, channels=channels, dtype=dtype,
                       callback=callback, **kwargs)
    with stream:
        while True:
            indata, status = await q_in.get()
            outdata = np.empty((buffer_size, channels), dtype=dtype)
            yield indata, outdata, status
            q_out.put_nowait(outdata)


async def stream_processor(callback, **kwargs):
    async for indata, outdata, status in stream_generator(**kwargs):
        outdata[:] = callback(indata)


async def main(**kwargs):
    asyncio.create_task(stream_processor(**kwargs))
    await asyncio.sleep(1e10)
