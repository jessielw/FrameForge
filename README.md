# Image-Generator

A CLI to generate comparison image sets with

## Usage

```
usage: Comparison Image Generator [-h] [-v] [--source SOURCE] [--encode ENCODE] [--image-dir IMAGE_DIR]
                                  [--indexer {lsmash,ffms2}] [--index-dir INDEX_DIR] [--sub-size SUB_SIZE]
                                  [--left-crop LEFT_CROP] [--right-crop RIGHT_CROP] [--top-crop TOP_CROP]
                                  [--bottom-crop BOTTOM_CROP] [--adv-resize-left ADV_RESIZE_LEFT]
                                  [--adv-resize-right ADV_RESIZE_RIGHT] [--adv-resize-top ADV_RESIZE_TOP]
                                  [--adv-resize-bottom ADV_RESIZE_BOTTOM] [--tone-map] [--re-sync RE_SYNC]
                                  [--comparison-count COMPARISON_COUNT] [--subtitle-color SUBTITLE_COLOR]
                                  [--release-sub-title RELEASE_SUB_TITLE]

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --source SOURCE       Path to source file
  --encode ENCODE       Path to encode file
  --image-dir IMAGE_DIR
                        Path to base image folder
  --indexer {lsmash,ffms2}
                        Indexer choice
  --index-dir INDEX_DIR
                        Path to look/create indexes
  --sub-size SUB_SIZE   Size of subtitles
  --left-crop LEFT_CROP
                        Left crop
  --right-crop RIGHT_CROP
                        Right crop
  --top-crop TOP_CROP   Top crop
  --bottom-crop BOTTOM_CROP
                        crop
  --adv-resize-left ADV_RESIZE_LEFT
                        Advanced resize left
  --adv-resize-right ADV_RESIZE_RIGHT
                        Advanced resize right
  --adv-resize-top ADV_RESIZE_TOP
                        Advanced resize top
  --adv-resize-bottom ADV_RESIZE_BOTTOM
                        Advanced resize bottom
  --tone-map            HDR tone-mapping
  --re-sync RE_SYNC     Sync offset for image generation in frames (i.e. --re-sync=-3)
  --comparison-count COMPARISON_COUNT
                        Amount of comparisons to generate
  --subtitle-color SUBTITLE_COLOR
                        Hex color code for subtitle color
  --release-sub-title RELEASE_SUB_TITLE
                        Release group subtitle name (this will show on the encode images)
```

## Supports

Windows 8 and up

## Requirements

You will need lsmash, ffms2, libfpng, libimwri, and SubText vapoursynth plugins.
Place all of these in a folder 'img_plugins' beside the script/executable.
