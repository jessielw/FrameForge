import sys
from pathlib import Path
from argparse import ArgumentParser
from frame_forge import GenerateImages
from frame_forge.exceptions import FrameForgeError
from frame_forge.utils import exit_application, restricted_int
from frame_forge.cli_utils import frame_list


program_name = "FrameForge"
__version__ = "1.4.0"


if __name__ == "__main__":
    parser = ArgumentParser(prog=program_name)

    parser.add_argument(
        "-v", "--version", action="version", version=f"{program_name} v{__version__}"
    )

    parser.add_argument("--source", type=str, help="Path to source file")
    parser.add_argument("--encode", type=str, help="Path to encode file")
    parser.add_argument(
        "--fpng-compression",
        type=int,
        choices=(0, 1, 2),
        default=1,
        help="fpng compression level (0 - fast, 1 - slow [default], 2 - uncompressed)",
    )
    parser.add_argument(
        "--frames",
        type=frame_list,
        help="Only use this if you want to specify the "
        "frames to generate, this disables sync frames",
    )
    parser.add_argument("--image-dir", type=str, help="Path to base image folder")
    parser.add_argument(
        "--indexer",
        type=str,
        choices=["lsmash", "ffms2"],
        default="lsmash",
        help="Indexer choice",
    )
    parser.add_argument(
        "--img-lib",
        type=str,
        choices=["imwri", "fpng"],
        default="fpng",
        help="Image library to use",
    )
    parser.add_argument(
        "--source-index-path", type=str, help="Path to look/create indexes for source"
    )
    parser.add_argument(
        "--encode-index-path", type=str, help="Path to look/create indexes for encode"
    )
    parser.add_argument("--left-crop", type=int, help="Left crop")
    parser.add_argument("--right-crop", type=int, help="Right crop")
    parser.add_argument("--top-crop", type=int, help="Top crop")
    parser.add_argument("--bottom-crop", type=int, help=" crop")
    parser.add_argument("--adv-resize-left", type=float, help="Advanced resize left")
    parser.add_argument("--adv-resize-right", type=float, help="Advanced resize right")
    parser.add_argument("--adv-resize-top", type=float, help="Advanced resize top")
    parser.add_argument(
        "--adv-resize-bottom", type=float, help="Advanced resize bottom"
    )
    parser.add_argument("--tone-map", action="store_true", help="HDR tone-mapping")
    parser.add_argument(
        "--re-sync",
        type=str,
        help="Sync offset for image generation in frames (i.e. --re-sync=-3)",
    )
    parser.add_argument(
        "--comparison-count", type=int, help="Amount of comparisons to generate"
    )
    parser.add_argument(
        "--start-trim",
        type=restricted_int(0, 100),
        default=12,
        help="Percentage to trim from start of media [choices 0 - 100] (defaults to 12%%)",
    )
    parser.add_argument(
        "--end-trim",
        type=restricted_int(0, 100),
        default=12,
        help="Percentage to trim from end of media [choices 0 - 100] (defaults to 12%%)",
    )
    parser.add_argument(
        "--sub-color",
        type=str,
        help='Hex color code for subtitle color (i.e. --sub-color "#fff000")',
    )
    parser.add_argument(
        "--sub-secondary-color",
        type=str,
        help='Hex color code for subtitle secondary color (i.e. --sub-color "#fff000")',
    )
    parser.add_argument(
        "--sub-outline-color",
        type=str,
        help='Hex color code for subtitle outline color (i.e. --sub-color "#fff000")',
    )
    parser.add_argument(
        "--sub-back-color",
        type=str,
        help='Hex color code for subtitle back color (i.e. --sub-color "#fff000")',
    )
    parser.add_argument("--sub-size", type=int, default=20, help="Size of subtitles")
    parser.add_argument(
        "--sub-alignment",
        type=int,
        default=7,
        choices=(1, 2, 3, 4, 5, 6, 7, 8, 9),
        help=(
            "Alignment of subtitles (Alignment values are based on the numeric "
            "keypad. 1 - bottom left, 2 - bottom center, 3 - bottom right, 4 - center left, "
            "5 - center center, 6 - center right, 7 - top left, 8 - top center, "
            "9 - top right. In addition to determining the position of the subtitle, "
            "this also determines the alignment of the text itself)"
        ),
    )
    parser.add_argument(
        "--sub-font-name",
        type=str,
        default="Segoe UI",
        help="Font name for subtitles",
    )
    parser.add_argument(
        "--sub-bold",
        type=int,
        default=1,
        choices=(0, 1),
        help="Bold formatting for subtitles (0=off, 1=on)",
    )
    parser.add_argument(
        "--sub-italic",
        type=int,
        default=0,
        choices=(0, 1),
        help="Italic formatting for subtitles (0=off, 1=on)",
    )
    parser.add_argument(
        "--sub-underline",
        type=int,
        default=0,
        choices=(0, 1),
        help="Underline formatting for subtitles (0=off, 1=on)",
    )
    parser.add_argument(
        "--sub-strikeout",
        type=int,
        default=0,
        choices=(0, 1),
        help="Strikeout formatting for subtitles (0=off, 1=on)",
    )
    parser.add_argument(
        "--sub-scale-x",
        type=restricted_int(1, 100),
        default=100,
        help="Subtitle X scale [choices 1 - 100] (defaults to '100')",
    )
    parser.add_argument(
        "--sub-scale-y",
        type=restricted_int(1, 100),
        default=100,
        help="Subtitle Y scale [choices 1 - 100] (defaults to '100')",
    )
    parser.add_argument(
        "--sub-spacing",
        type=int,
        default=0,
        help="Subtitle spacing (defaults to '0')",
    )
    parser.add_argument(
        "--sub-border-style",
        type=int,
        choices=(0, 1, 3),
        default=0,
        help="Subtitle border style (0=off, 1=outline, 3=opaque box) [defaults to '0']",
    )
    parser.add_argument(
        "--sub-outline-width",
        type=int,
        default=1,
        help="Subtitle outline width (defaults to '1')",
    )
    parser.add_argument(
        "--sub-shadow-depth",
        type=int,
        default=0,
        help="Subtitle shadow depth (defaults to '0')",
    )
    parser.add_argument(
        "--sub-left-margin",
        type=int,
        default=10,
        help="Subtitle left margin (defaults to '10')",
    )
    parser.add_argument(
        "--sub-right-margin",
        type=int,
        default=10,
        help="Subtitle right margin (defaults to '10')",
    )
    parser.add_argument(
        "--sub-vertical-margin",
        type=int,
        default=10,
        help="Subtitle vertical margin (defaults to '10')",
    )
    parser.add_argument(
        "--source-sub-title",
        type=str,
        default="Source",
        help="Source group subtitle name (this will show on the source images)",
    )
    parser.add_argument(
        "--encode-sub-title",
        "--release-sub-title",
        type=str,
        default="Encode",
        dest="encode_sub_title",
        help="Release group subtitle name (this will show on the encode images)",
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        exit_application("", 1)

    if not args.source or not Path(args.source).is_file():
        exit_application(
            "Source input is not detected (--source 'path to file')",
            1,
        )

    if not args.encode or not Path(args.encode).is_file():
        exit_application(
            "Encode input is not detected (--encode 'path to file')",
            1,
        )

    index_suffix = ".lwi" if args.indexer == "lsmash" else ".ffindex"
    for index_input in [args.source_index_path, args.encode_index_path]:
        if index_input:
            if Path(index_input).suffix != index_suffix:
                exit_application(
                    f"When using {args.indexer} indexer you must use '{index_suffix}' "
                    "for your source/encode index path suffix",
                    1,
                )

    if args.image_dir:
        image_dir = Path(args.image_dir)
    else:
        image_dir = Path(Path(args.encode).parent / f"{Path(args.encode).stem}_images")
    image_dir.mkdir(parents=True, exist_ok=True)

    # deprecations
    # TODO: remove support for this arg in the future
    if "--release-sub-title" in sys.argv:
        print(
            "WARNING: '--release-sub-title' is deprecated and will be removed in a future version. "
            "Use '--encode-sub-title' instead.",
            file=sys.stderr,
        )

    try:
        img_generator = GenerateImages(
            source_file=Path(args.source),
            encode_file=Path(args.encode),
            fpng_compression=args.fpng_compression,
            frames=args.frames,
            image_dir=image_dir,
            indexer=args.indexer,
            img_lib=args.img_lib,
            source_index_path=args.source_index_path,
            encode_index_path=args.encode_index_path,
            left_crop=args.left_crop,
            right_crop=args.right_crop,
            top_crop=args.top_crop,
            bottom_crop=args.bottom_crop,
            adv_resize_left=args.adv_resize_left,
            adv_resize_right=args.adv_resize_right,
            adv_resize_top=args.adv_resize_top,
            adv_resize_bottom=args.adv_resize_bottom,
            tone_map=args.tone_map,
            re_sync=args.re_sync,
            comparison_count=int(args.comparison_count)
            if args.comparison_count
            else 20,
            start_trim=int(args.start_trim),
            end_trim=int(args.end_trim),
            sub_size=args.sub_size,
            sub_alignment=args.sub_alignment,
            sub_color=args.sub_color,
            sub_secondary_color=args.sub_secondary_color,
            sub_outline_color=args.sub_outline_color,
            sub_back_color=args.sub_back_color,
            sub_font_name=args.sub_font_name,
            sub_bold=args.sub_bold,
            sub_italic=args.sub_italic,
            sub_underline=args.sub_underline,
            sub_strikeout=args.sub_strikeout,
            sub_scale_x=args.sub_scale_x,
            sub_scale_y=args.sub_scale_y,
            sub_spacing=args.sub_spacing,
            sub_border_style=args.sub_border_style,
            sub_outline_width=args.sub_outline_width,
            sub_shadow_depth=args.sub_shadow_depth,
            sub_left_margin=args.sub_left_margin,
            sub_right_margin=args.sub_right_margin,
            sub_vertical_margin=args.sub_vertical_margin,
            source_sub_title=args.source_sub_title,
            release_sub_title=args.encode_sub_title,
        )
        if img_generator:
            try:
                img_gen = img_generator.process_images()
                if img_gen:
                    exit_application(f"\nOutput: {img_gen}", 0)
            except FrameForgeError as ff_error:
                img_generator.clean_temp(False)
                exit_application(str(ff_error), 1)
            except Exception as except_error:
                img_generator.clean_temp(False)
                exit_application(f"Unhandled Exception: {except_error}", 1)
            except KeyboardInterrupt:
                img_generator.clean_temp(False)
                exit_application("KeyboardInterrupt, exiting...", 1)
            finally:
                img_generator.clean_temp(False)
    except Exception as init_error:
        exit_application(f"Initiation Error: {init_error}", 1)
