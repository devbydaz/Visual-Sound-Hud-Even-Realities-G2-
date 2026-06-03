import asyncio
import websockets
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import csv
import time

model = hub.load('https://tfhub.dev/google/yamnet/1')

class_map_path = model.class_map_path().numpy()
class_names = []
with tf.io.gfile.GFile(class_map_path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        class_names.append(row['display_name'])

async def audio_handler(websocket):
    buffer = np.array([], dtype=np.float32)
    GAIN_MULTIPLIER = 3.0 
    
    last_sound = ""
    lockout_until = 0.0

    try:
        async for message in websocket:
            raw_audio = np.frombuffer(message, dtype=np.int16).astype(np.float32) / 32768.0
            audio_data = np.clip(raw_audio * GAIN_MULTIPLIER, -1.0, 1.0)
            buffer = np.concatenate((buffer, audio_data))

            if len(buffer) >= 15600:
                chunk = buffer[:15600]
                buffer = buffer[15600:]

                scores, embeddings, spectrogram = model(chunk)
                top_class_index = tf.math.argmax(scores[0]).numpy()
                top_score = scores[0][top_class_index].numpy()
                top_class_name = class_names[top_class_index]
                
                current_time = time.time()

                if top_score > 0.30:
                    if top_class_name == last_sound:
                        lockout_until = current_time + 1.5
                        await websocket.send(f"{top_class_name.upper()} ({int(top_score*100)}%)")
                    
                    else:
                        if current_time > lockout_until or top_score > 0.65:
                            last_sound = top_class_name
                            lockout_until = current_time + 1.5 
                            await websocket.send(f"{top_class_name.upper()} ({int(top_score*100)}%)")

    except websockets.exceptions.ConnectionClosed:
        pass

async def main():
    async with websockets.serve(audio_handler, "0.0.0.0", 8765):
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
