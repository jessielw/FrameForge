# Image-Generator

A CLI to generate comparison image sets utilizing the power of VapourSynth

## Usage

```
usage: FrameForge [-h] [-v] [--source SOURCE] [--encode ENCODE] [--fpng-compression {0,1,2}] [--frames FRAMES]
                  [--image-dir IMAGE_DIR] [--indexer {lsmash,ffms2}] [--img-lib {imwri,fpng}]
                  [--source-index-path SOURCE_INDEX_PATH] [--encode-index-path ENCODE_INDEX_PATH] [--left-crop LEFT_CROP]
                  [--right-crop RIGHT_CROP] [--top-crop TOP_CROP] [--bottom-crop BOTTOM_CROP]
                  [--adv-resize-left ADV_RESIZE_LEFT] [--adv-resize-right ADV_RESIZE_RIGHT]
                  [--adv-resize-top ADV_RESIZE_TOP] [--adv-resize-bottom ADV_RESIZE_BOTTOM] [--tone-map]
                  [--re-sync RE_SYNC] [--comparison-count COMPARISON_COUNT] [--sub-color SUB_COLOR]
                  [--sub-secondary-color SUB_SECONDARY_COLOR] [--sub-outline-color SUB_OUTLINE_COLOR]
                  [--sub-back-color SUB_BACK_COLOR] [--sub-size SUB_SIZE] [--sub-alignment SUB_ALIGNMENT]
                  [--sub-font-name SUB_FONT_NAME] [--sub-bold {0,1}] [--sub-italic {0,1}] [--sub-underline {0,1}]
                  [--sub-strikeout {0,1}] [--sub-scale-x SUB_SCALE_X] [--sub-scale-y SUB_SCALE_Y]
                  [--sub-spacing SUB_SPACING] [--sub-border-style {0,1,3}] [--sub-outline-width SUB_OUTLINE_WIDTH]
                  [--sub-shadow-depth SUB_SHADOW_DEPTH] [--sub-left-margin SUB_LEFT_MARGIN]
                  [--sub-right-margin SUB_RIGHT_MARGIN] [--sub-vertical-margin SUB_VERTICAL_MARGIN]
                  [--source-sub-title SOURCE_SUB_TITLE] [--encode-sub-title ENCODE_SUB_TITLE]

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --source SOURCE       Path to source file
  --encode ENCODE       Path to encode file
  --fpng-compression {0,1,2}
                        fpng compression level (0 - fast, 1 - slow [default], 2 - uncompressed)
  --frames FRAMES       Only use this if you want to specify the frames to generate, this disables sync frames
  --image-dir IMAGE_DIR
                        Path to base image folder
  --indexer {lsmash,ffms2}
                        Indexer choice
  --img-lib {imwri,fpng}
                        Image library to use
  --source-index-path SOURCE_INDEX_PATH
                        Path to look/create indexes for source
  --encode-index-path ENCODE_INDEX_PATH
                        Path to look/create indexes for encode
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
  --sub-color SUB_COLOR
                        Hex color code for subtitle color (i.e. --sub-color "#fff000")
  --sub-secondary-color SUB_SECONDARY_COLOR
                        Hex color code for subtitle secondary color (i.e. --sub-color "#fff000")
  --sub-outline-color SUB_OUTLINE_COLOR
                        Hex color code for subtitle outline color (i.e. --sub-color "#fff000")
  --sub-back-color SUB_BACK_COLOR
                        Hex color code for subtitle back color (i.e. --sub-color "#fff000")
  --sub-size SUB_SIZE   Size of subtitles
  --sub-alignment SUB_ALIGNMENT
                        Alignment of subtitles (.ass)
  --sub-font-name SUB_FONT_NAME
                        Font name for subtitles
  --sub-bold {0,1}      Bold formatting for subtitles (0=off, 1=on)
  --sub-italic {0,1}    Italic formatting for subtitles (0=off, 1=on)
  --sub-underline {0,1}
                        Underline formatting for subtitles (0=off, 1=on)
  --sub-strikeout {0,1}
                        Strikeout formatting for subtitles (0=off, 1=on)
  --sub-scale-x SUB_SCALE_X
                        Subtitle X scale [choices 1 - 100] (defaults to '100')
  --sub-scale-y SUB_SCALE_Y
                        Subtitle Y scale [choices 1 - 100] (defaults to '100')
  --sub-spacing SUB_SPACING
                        Subtitle spacing (defaults to '0')
  --sub-border-style {0,1,3}
                        Subtitle border style (0=off, 1=outline, 3=opaque box) [defaults to '0']
  --sub-outline-width SUB_OUTLINE_WIDTH
                        Subtitle outline width (defaults to '1')
  --sub-shadow-depth SUB_SHADOW_DEPTH
                        Subtitle shadow depth (defaults to '0')
  --sub-left-margin SUB_LEFT_MARGIN
                        Subtitle left margin (defaults to '10')
  --sub-right-margin SUB_RIGHT_MARGIN
                        Subtitle right margin (defaults to '10')
  --sub-vertical-margin SUB_VERTICAL_MARGIN
                        Subtitle vertical margin (defaults to '10')
  --source-sub-title SOURCE_SUB_TITLE
                        Source group subtitle name (this will show on the source images)
  --encode-sub-title ENCODE_SUB_TITLE, --release-sub-title ENCODE_SUB_TITLE
                        Release group subtitle name (this will show on the encode images)
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
