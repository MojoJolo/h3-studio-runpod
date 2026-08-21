#!/bin/sh
# One-time setup: clones and builds the h3.c engine, prepares folders.
set -e
cd "$(dirname "$0")"

if ! xcode-select -p >/dev/null 2>&1; then
  echo "Xcode Command Line Tools required: run  xcode-select --install"; exit 1
fi
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
  echo "ffmpeg/ffprobe required: brew install ffmpeg"; exit 1
fi

if [ ! -d engine ]; then
  echo "Cloning antirez/h3.c ..."
  git clone https://github.com/antirez/h3.c engine
fi
echo "Building h3 ..."
(cd engine && make -j8)
ln -sfn engine/h3_shaders.metal h3_shaders.metal
cat > h3 << 'WRAP'
#!/bin/sh
exec "$(dirname "$0")/engine/h3" "$@"
WRAP
chmod +x h3
mkdir -p inputs outputs

echo ""
echo "Setup complete. Next: download the MiniMax-H3 weights (see README),"
echo "place them in ./MiniMax-H3, then run:  ./studio"
