from pathlib import Path
from argparse import ArgumentParser
from frame_forge import GenerateImages
from frame_forge.exceptions import FrameForgeError
from frame_forge.utils import exit_application
from frame_forge.cli_utils import frame_list


program_name = "FrameForge"
__version__ = "1.1.0"


if __name__ == "__main__":
    parser = ArgumentParser(prog=program_name)

    parser.add_argument(
        "-v", "--version", action="version", version=f"{program_name} v{__version__}"
    )

    parser.add_argument("--source", type=str, help="Path to source file")
    parser.add_argument("--encode", type=str, help="Path to encode file")
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
        help="Indexer choice",
    )
    parser.add_argument("--index-dir", type=str, help="Path to look/create indexes")
    parser.add_argument("--sub-size", type=int, default=20, help="Size of subtitles")
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
        "--subtitle-color", type=str, help="Hex color code for subtitle color"
    )
    parser.add_argument(
        "--release-sub-title",
        type=str,
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

    if args.image_dir:
        image_dir = Path(args.image_dir)
    else:
        image_dir = Path(Path(args.encode).parent / f"{Path(args.encode).stem}_images")
    image_dir.mkdir(parents=True, exist_ok=True)

    try:
        img_generator = GenerateImages(
            source_file=Path(args.source),
            encode_file=Path(args.encode),
            frames=args.frames,
            image_dir=image_dir,
            indexer=args.indexer,
            index_directory=args.index_dir,
            sub_size=args.sub_size,
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
            subtitle_color=args.subtitle_color,
            release_sub_title=args.release_sub_title,
        )
        img_gen = img_generator.process_images()
        if img_gen:
            exit_application(f"Output: {img_gen}", 0)
    except FrameForgeError as error:
        exit_application(error, 1)
