#!/bin/bash

DUR=""

for entry in $PWD/audio/sarah/*
do
  if [ -f "$entry" ];then
    DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $entry)
    echo "$(basename $entry) - $DUR"
  fi
done