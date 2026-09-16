#!/bin/sh
# Texte → MP3 avec espeak-ng (voix française), pour écouter le plan en auto.
#
# La voix est robotique : espeak-ng est un synthétiseur par formants, pas une
# voix neuronale. C'est le seul moteur installable sans accès réseau sortant.
# Pour une meilleure voix, ouvrir plutôt le texte dans Chrome (« Écouter cette
# page ») ou dans une application de livres, qui utilisent les voix du système.
#
# Prérequis : apt-get install espeak-ng ; pip install lameenc
# Usage : ./faire_audio.sh <texte.txt> <sortie.mp3> [mots_par_minute]

set -eu
[ $# -ge 2 ] || { echo "Usage : $0 <texte.txt> <sortie.mp3> [mots_par_minute]" >&2; exit 1; }
SRC=$1
DST=$2
VITESSE=${3:-160}
WAV=$(mktemp -t havana_audio_XXXXXX.wav)
trap 'rm -f "$WAV"' EXIT

espeak-ng -v fr-fr -s "$VITESSE" -f "$SRC" -w "$WAV"

python3 - "$WAV" "$DST" <<'PY'
import sys, wave, lameenc

src, dst = sys.argv[1], sys.argv[2]
with wave.open(src) as w:
    pcm = w.readframes(w.getnframes())
    secondes = w.getnframes() / w.getframerate()
    enc = lameenc.Encoder()
    enc.set_bit_rate(56)          # parole mono : 56 kbps suffit largement
    enc.set_in_sample_rate(w.getframerate())
    enc.set_channels(1)
    enc.set_quality(2)
    data = bytes(enc.encode(pcm) + enc.flush())
with open(dst, "wb") as f:
    f.write(data)
print(f"{dst} — {int(secondes // 60)} min {int(secondes % 60):02d} s, {len(data) / 1e6:.1f} Mo")
PY
