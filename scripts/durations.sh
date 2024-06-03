for entry in $PWD/audio/sarah/*
do
  if [ -f "$entry" ];then
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $entry
  fi
done