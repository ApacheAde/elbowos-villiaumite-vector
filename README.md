# Villiaumite Vector

Full-colour Python 3 neon light-cycle arcade for [ElbowOS](https://x.com/ElbowOS).

Steer a vermillion cycle across a wine-dark grid. Your trail is a wall. Chartreuse and azure rivals weave their own. Amber shards raise the combo. Crash and you respawn — the board keeps filling.

Not a ROM, not an emulator, not a clone of the prior ElbowOS packs (shuttle, asteroid arc, tide hopper).

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 villiaumite_vector.py --play
```

Arrows or WASD turn. R restarts. Esc quits.

## Record a 9:16 reel

```bash
python3 villiaumite_vector.py
```

Headless path uses `SDL_VIDEODRIVER=dummy`, draws a 1080x1920 surface, and pipes 15 seconds at 30fps to ffmpeg (`libx264`, `yuv420p`, CRF 20, `+faststart`).

Override the output path with `ELBOWOS_MP4`.

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1ovfUUW5j53MreNEEsShIXNnr7bAkINIr/view
- Posted copy: https://drive.google.com/file/d/19yyT-UXVFCDzUJDYxjlrR68k-yBIlqNs/view
