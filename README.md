# Image-Generator

A CLI to generate comparison image sets with

## Usage

```
usage: FrameForge [-h] [-v] [--source SOURCE] [--encode ENCODE] [--frames FRAMES]
                  [--image-dir IMAGE_DIR] [--indexer {lsmash,ffms2}]
                  [--index-dir INDEX_DIR] [--sub-size SUB_SIZE] [--left-crop LEFT_CROP]
                  [--right-crop RIGHT_CROP] [--top-crop TOP_CROP]
                  [--bottom-crop BOTTOM_CROP] [--adv-resize-left ADV_RESIZE_LEFT]
                  [--adv-resize-right ADV_RESIZE_RIGHT]
                  [--adv-resize-top ADV_RESIZE_TOP]
                  [--adv-resize-bottom ADV_RESIZE_BOTTOM] [--tone-map]
                  [--re-sync RE_SYNC] [--comparison-count COMPARISON_COUNT]
                  [--subtitle-color SUBTITLE_COLOR]
                  [--release-sub-title RELEASE_SUB_TITLE]

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --source SOURCE       Path to source file
  --encode ENCODE       Path to encode file
  --frames FRAMES       Only use this if you want to specify the frames to generate,
                        this disables sync frames
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
                        Release group subtitle name (this will show on the encode
                        images)
```

## Supports

Windows 8 and up (x64).
Technically could support Linux/MacOS but binaries will only be compiled for Windows for now.

## Requirements

You will need lsmash, ffms2, libfpng, libimwri, and SubText vapoursynth plugins. For windows
I have compiled an executable with the needed runtime libraries.

## Example Usage

```
FrameForge.exe --source "path/Ant-Man.2015.mkv" --encode "path/Ant-Man.2015.Encoded.mkv" --sub-size 12 --indexer lsmash --top-crop 22 --bottom-crop 22 --subtitle-color #00FF00

Indexing source
...
Source index completed

Indexing encode
...
Encode index completed

Checking if encode has been de-interlaced
No de-interlacing detected

Generating 20 'B' frames for comparison images
Finished generating 20 'B' frames

Creating folders for images
Folder creation completed

Generating screenshots, please wait
Writing file: 01a_source__%d.png, frame: 25270
Writing file: 02a_source__%d.png, frame: 30590
...

Generating a few sync frames
Writing file: 01b_encode__%d.png, frame: 35910
Writing file: 02b_encode__%d.png, frame: 25270
...

Screen generation completed
Output: path/Ant-Man.2015_images/
```

[![04a_source__41230.png](https://thumbs2.imgbox.com/8d/47/X3l54wjy_t.png)](https://imgbox.com/X3l54wjy)
[![04b_encode__41230.png](https://thumbs2.imgbox.com/07/65/WvJ55AZp_t.png)](https://imgbox.com/WvJ55AZp)

[![11a_source__41230.png](https://thumbs2.imgbox.com/59/bd/woQpbay2_t.png)](https://imgbox.com/woQpbay2)
[![11b_encode__41230.png](https://thumbs2.imgbox.com/96/24/WzCtO3dY_t.png)](https://imgbox.com/WzCtO3dY)

[![16a_source__41230.png](https://thumbs2.imgbox.com/a8/5b/GftN1tCw_t.png)](https://imgbox.com/GftN1tCw)
[![16b_encode__41230.png](https://thumbs2.imgbox.com/c2/94/tFhRztHT_t.png)](https://imgbox.com/tFhRztHT)
