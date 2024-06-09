#!/bin/bash

DUR=""

echo "001: VOICE"
echo ""

for entry in $PWD/audio/001/*
do
  if [ -f "$entry" ];then
    DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $entry)
    echo "$(basename $entry) - $DUR"
  fi
done

echo ""
echo "002: GUN"
echo ""

for entry in $PWD/audio/002/*
do
  if [ -f "$entry" ];then
    DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $entry)
    echo "$(basename $entry) - $DUR"
  fi
done
