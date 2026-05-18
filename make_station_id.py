import asyncio
import edge_tts

async def main():
    tts = edge_tts.Communicate(
        "The Long View. Thinking out loud, all day long.",
        "en-US-AriaNeural"
    )
    await tts.save("audio/assets/jingles/station_id.mp3")
    print("Station ID created.")

asyncio.run(main())
