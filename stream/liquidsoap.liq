#!/usr/bin/env liquidsoap
# The Long View — Liquidsoap master schedule
# Fallback chain: scheduled segment → music library → archive → station ID

settings.server.telnet.set(true)
settings.server.telnet.port.set(1234)

# Paths — update to match your Oracle Cloud deploy path
segments_dir = "/home/ubuntu/the-long-view/audio/assets/output/segments"
music_dir    = "/home/ubuntu/the-long-view/audio/assets/music"
jingles_dir  = "/home/ubuntu/the-long-view/audio/assets/jingles"
archive_dir  = "/home/ubuntu/the-long-view/audio/assets/output/archive"

# Sources
scheduled  = playlist(mode="normal", reload=10, reload_mode="watch", segments_dir)
music_lib  = playlist(mode="randomize", music_dir)
archive    = playlist(mode="randomize", archive_dir)
station_id = single(jingles_dir ^ "/station_id.mp3")

# Fallback chain — never silent
radio = fallback(track_sensitive=false, [
  scheduled,
  music_lib,
  archive,
  station_id,
])

# Inject Ko-fi link into stream metadata
radio = map_metadata(fun(m) -> [
  ("title",   m["title"]),
  ("artist",  "Aria — The Long View"),
  ("comment", "Support the station: YOUR_KOFI_URL"),
], radio)

# Output to Icecast
output.icecast(%mp3(bitrate=128),
  host     = "localhost",
  port     = 8000,
  password = "3udyxjtMpkV412!xb",
  mount    = "/stream",
  name        = "The Long View",
  description = "Thinking out loud, all day long.",
  genre       = "Talk / Ideas",
  url         = "https://clifford-smith.github.io/the-long-view",
  radio)
