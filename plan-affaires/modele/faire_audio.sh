#!/bin/sh
# Texte → MP3, pour écouter le plan en auto.
#
# Utilise la voix neuronale Piper si le modèle est présent, sinon retombe sur
# espeak-ng, dont la voix par formants est nettement moins agréable.
#
# Installation :
#   pip install piper-tts lameenc
#   apt-get install espeak-ng          # phonémisation (et voix de secours)
#   curl -sL -o voix.tar.gz https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-fr-siwis-medium.tar.gz
#   tar xzf voix.tar.gz                # -> fr-siwis-medium.onnx et .onnx.json
#
# Le modèle vient de GitHub : le proxy des sessions en nuage bloque
# HuggingFace, où sont hébergées les voix Piper récentes.
#
# Usage : ./faire_audio.sh <texte.txt> <sortie.mp3> [dossier_du_modele]

set -eu
[ $# -ge 2 ] || { echo "Usage : $0 <texte.txt> <sortie.mp3> [dossier_du_modele]" >&2; exit 1; }
SRC=$1
DST=$2
MODELES=${3:-.}
VOIX="$MODELES/fr-siwis-medium.onnx"
WAV=$(mktemp -t havana_audio_XXXXXX.wav)
trap 'rm -f "$WAV"' EXIT

if [ -f "$VOIX" ]; then
    echo "Voix neuronale Piper (fr-siwis-medium) — comptez environ une minute de calcul par minute d'audio."
    piper -m "$VOIX" -c "$VOIX.json" -f "$WAV" < "$SRC"
else
    echo "Modèle Piper absent de $MODELES : repli sur espeak-ng (voix robotique)." >&2
    espeak-ng -v fr-fr -s 160 -f "$SRC" -w "$WAV"
fi

python3 - "$WAV" "$DST" <<'PY'
import sys, wave, lameenc

src, dst = sys.argv[1], sys.argv[2]
with wave.open(src) as w:
    pcm = w.readframes(w.getnframes())
    secondes = w.getnframes() / w.getframerate()
    enc = lameenc.Encoder()
    enc.set_bit_rate(64)          # parole mono : 64 kbps garde la voix nette
    enc.set_in_sample_rate(w.getframerate())
    enc.set_channels(1)
    enc.set_quality(2)
    data = bytes(enc.encode(pcm) + enc.flush())
with open(dst, "wb") as f:
    f.write(data)
print(f"{dst} — {int(secondes // 60)} min {int(secondes % 60):02d} s, {len(data) / 1e6:.1f} Mo")
PY
