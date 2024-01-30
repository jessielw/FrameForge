import re
import shutil
from random import choice
from pathlib import Path
from typing import Tuple
from numpy import linspace
from unidecode import unidecode
import awsmfunc
import vapoursynth as vs
from frame_forge.exceptions import FrameForgeError
from frame_forge.font_scaler import FontScaler
from frame_forge.utils import get_working_dir, hex_to_bgr


class GenerateImages:
    def __init__(
        self,
        source_file: Path,
        encode_file: Path,
        image_dir: Path,
        indexer: str,
        index_directory: None | str,
        sub_size: int,
        left_crop: int,
        right_crop: int,
        top_crop: int,
        bottom_crop: int,
        adv_resize_left: float,
        adv_resize_right: float,
        adv_resize_top: float,
        adv_resize_bottom: float,
        tone_map: bool,
        re_sync: str,
        comparison_count: int,
        subtitle_color: str,
        release_sub_title: str | None,
    ):
        self.source_file = source_file
        self.source_node = None
        self.reference_source_file = None
        self.encode_file = encode_file
        self.encode_node = None
        self.image_dir = image_dir
        self.indexer = indexer
        self.index_dir = index_directory
        self.sub_size = sub_size
        self.left_crop = left_crop
        self.right_crop = right_crop
        self.top_crop = top_crop
        self.bottom_crop = bottom_crop
        self.adv_resize_left = adv_resize_left
        self.adv_resize_right = adv_resize_right
        self.adv_resize_top = adv_resize_top
        self.adv_resize_bottom = adv_resize_bottom
        self.tone_map = tone_map
        self.re_sync = re_sync
        self.comparison_count = comparison_count
        self.subtitle_color = subtitle_color
        self.release_sub_title = release_sub_title

        self.core = vs.core
        self.load_plugins()

    def process_images(self):
        if self.indexer == "lsmash":
            self.index_lsmash()

        elif self.indexer == "ffms2":
            self.index_ffms2()

        num_source_frames = len(self.source_node)
        num_encode_frames = len(self.encode_node)

        # Format: Name, Fontname, Font-size, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic,
        # Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL,
        # MarginR, MarginV,

        # bgr color
        color = "&H000ac7f5"
        if self.subtitle_color:
            color = hex_to_bgr(self.subtitle_color)

        selected_sub_style = (
            f"Segoe UI,{self.sub_size},{color},&H00000000,&H00000000,&H00000000,"
            "1,0,0,0,100,100,0,0,1,1,0,7,5,0,0,1"
        )

        selected_sub_style_ref, selected_sub_style_sync = self.sync_font_scaling(
            num_source_frames=num_source_frames, scaling_factor=1.35
        )

        self.check_de_interlaced(num_source_frames, num_encode_frames)

        b_frames = self.get_b_frames(num_source_frames)

        screenshot_comparison_dir, screenshot_sync_dir = self.generate_folders()

        self.handle_crop()

        self.handle_resize()

        self.handle_hdr()

        vs_source_info, vs_encode_info = self.handle_subtitles(selected_sub_style)

        img_job = self.generate_screens(
            b_frames,
            vs_source_info,
            vs_encode_info,
            screenshot_comparison_dir,
            screenshot_sync_dir,
            selected_sub_style_ref,
            selected_sub_style_sync,
        )

        return img_job

    @staticmethod
    def screen_gen_callback(sg_call_back):
        print(
            str(sg_call_back).replace("ScreenGen: ", "").replace("\n", "").strip(),
            flush=True,
        )

    def sync_font_scaling(
        self, num_source_frames, scaling_factor: float
    ) -> Tuple[str, str]:
        calculate_str_len = max(
            len("frame: reference"), len(str(f"frame: {num_source_frames}"))
        )
        sync_size_offset = 5
        scale_position = FontScaler().get_adjusted_scale(
            self.sub_size + sync_size_offset, scaling_factor
        )
        calculate_right_subs = int(
            self.source_node.width
            - ((calculate_str_len + self.sub_size + sync_size_offset) * scale_position)
        )
        selected_sub_style_ref = (
            f"Segoe UI,{self.sub_size + sync_size_offset},&H31FF31&,&H00000000,&H00000000,&H00000000,"
            f"1,0,0,0,100,100,0,0,1,1,0,7,5,0,0,1"
        )
        selected_sub_style_sync = (
            f"Segoe UI,{self.sub_size + sync_size_offset},&H31FF31&,&H00000000,&H00000000,&H00000000,"
            f"1,0,0,0,100,100,0,0,1,1,0,7,{calculate_right_subs},0,0,1"
        )
        return selected_sub_style_ref, selected_sub_style_sync

    def generate_ref_screens(
        self, selected_sub_style_ref, frames: list, screenshot_sync_dir
    ):
        """Generates reference frames"""
        for ref_frame in frames:
            vs_encode_ref_info = self.core.sub.Subtitle(
                clip=self.encode_node,
                text=f"Reference\nFrame: {ref_frame}",
                style=selected_sub_style_ref,
            )
            awsmfunc.ScreenGen(
                vs_encode_ref_info,
                frame_numbers=[ref_frame],
                fpng_compression=1,
                folder=screenshot_sync_dir,
                suffix="b_encode__%d",
                callback=self.screen_gen_callback,
            )

    def generate_sync_screens(
        self, frame_list, selected_sub_style_sync, screenshot_sync_dir
    ):
        """Generates sync frames"""
        for sync_frame in frame_list:
            vs_sync_info = self.core.sub.Subtitle(
                clip=self.source_node,
                text=f"Sync\nFrame: {sync_frame}",
                style=selected_sub_style_sync,
            )
            awsmfunc.ScreenGen(
                vs_sync_info,
                frame_numbers=[sync_frame],
                fpng_compression=1,
                folder=Path(screenshot_sync_dir),
                suffix="a_source__%d",
                callback=self.screen_gen_callback,
            )

    def generate_screens(
        self,
        b_frames,
        vs_source_info,
        vs_encode_info,
        screenshot_comparison_dir,
        screenshot_sync_dir,
        selected_sub_style_ref,
        selected_sub_style_sync,
    ) -> str:
        print("\nGenerating screenshots, please wait", flush=True)

        # handle re_sync if needed
        sync_frames = []
        if self.re_sync:
            get_sync_digits = re.search(r"(\d+)", self.re_sync)
            sync_digits = int(get_sync_digits.group(1)) if get_sync_digits else 0
            for x_frames in b_frames:
                if self.re_sync.startswith("-"):
                    sync_frames.append(int(x_frames) - sync_digits)
                else:
                    sync_frames.append(int(x_frames) + sync_digits)
        else:
            sync_frames = b_frames

        # generate source images
        awsmfunc.ScreenGen(
            vs_source_info,
            frame_numbers=sync_frames,
            fpng_compression=1,
            folder=screenshot_comparison_dir,
            suffix="a_source__%d",
            callback=self.screen_gen_callback,
        )

        # generate encode images
        awsmfunc.ScreenGen(
            vs_encode_info,
            frame_numbers=b_frames,
            fpng_compression=1,
            folder=screenshot_comparison_dir,
            suffix="b_encode__%d",
            callback=self.screen_gen_callback,
        )

        # generate some sync frames
        print("\nGenerating a few sync frames", flush=True)

        # select two frames randomly from list
        get_sync_1 = choice(b_frames)
        remove_sync1 = b_frames.copy()
        remove_sync1.remove(get_sync_1)
        get_sync_2 = choice(remove_sync1)

        # sync list
        ref_sync_list = sorted([get_sync_1, get_sync_2])

        # reference subs
        self.generate_ref_screens(
            selected_sub_style_ref, ref_sync_list, screenshot_sync_dir
        )

        # sync subs 1
        sync_subs_1 = [ref_sync_list[0] + i for i in range(-5, 6)]

        self.generate_sync_screens(
            sync_subs_1,
            selected_sub_style_sync,
            Path(Path(screenshot_sync_dir) / "sync1"),
        )

        # sync subs 2
        sync_subs_2 = [ref_sync_list[1] + i for i in range(-5, 6)]

        self.generate_sync_screens(
            sync_subs_2,
            selected_sub_style_sync,
            Path(Path(screenshot_sync_dir) / "sync2"),
        )

        print("Screen generation completed", flush=True)
        return str(screenshot_comparison_dir)

    def handle_subtitles(self, selected_sub_style):
        vs_source_info = self.core.sub.Subtitle(
            clip=self.source_node, text="Source", style=selected_sub_style
        )
        vs_encode_info = awsmfunc.FrameInfo(
            clip=self.encode_node,
            title=self.release_sub_title if self.release_sub_title else "",
            style=selected_sub_style,
        )

        return vs_source_info, vs_encode_info

    def handle_hdr(self):
        if self.tone_map:
            self.source_node = awsmfunc.DynamicTonemap(
                clip=self.source_node, libplacebo=False
            )
            self.encode_node = awsmfunc.DynamicTonemap(
                clip=self.encode_node,
                reference=self.reference_source_file,
                libplacebo=False,
            )

    def handle_resize(self):
        if (
            self.source_node.width != self.encode_node.width
            and self.source_node.height != self.encode_node.height
            or any(
                [
                    self.adv_resize_left,
                    self.adv_resize_right,
                    self.adv_resize_top,
                    self.adv_resize_bottom,
                ]
            )
        ):
            # advanced resize offset vars
            advanced_resize_left = self.adv_resize_left if self.adv_resize_left else 0
            advanced_resize_top = self.adv_resize_top if self.adv_resize_top else 0
            advanced_resize_width = (
                self.adv_resize_right if self.adv_resize_right else 0
            )
            advanced_resize_height = (
                self.adv_resize_bottom if self.adv_resize_bottom else 0
            )

            # resize source to match encode for screenshots
            self.source_node = self.core.resize.Spline36(
                self.source_node,
                width=int(self.encode_node.width),
                height=int(self.encode_node.height),
                src_left=advanced_resize_left,
                src_top=advanced_resize_top,
                src_width=float(
                    self.source_node.width
                    - (advanced_resize_left + advanced_resize_width)
                ),
                src_height=float(
                    self.source_node.height
                    - (advanced_resize_top + advanced_resize_height)
                ),
                dither_type="error_diffusion",
            )

    def handle_crop(self):
        if any([self.left_crop, self.right_crop, self.top_crop, self.bottom_crop]):
            self.source_node = self.core.std.Crop(
                self.source_node,
                left=self.left_crop if self.left_crop else 0,
                right=self.right_crop if self.right_crop else 0,
                top=self.top_crop if self.top_crop else 0,
                bottom=self.bottom_crop if self.bottom_crop else 0,
            )

    def generate_folders(self):
        print("\nCreating folders for images", flush=True)
        if self.image_dir:
            image_output_dir = Path(self.image_dir)
        else:
            image_output_dir = Path(
                Path(self.encode_file).parent / f"{Path(self.encode_file).stem}_images"
            )

        # remove any accent characters from path
        image_output_dir = Path(unidecode(str(image_output_dir)))

        # check if temp image dir exists, if so delete it!
        if image_output_dir.exists():
            shutil.rmtree(image_output_dir, ignore_errors=True)

        # create main image dir
        image_output_dir.mkdir(exist_ok=True, parents=True)

        # create comparison image directory and define it as variable
        Path(Path(image_output_dir) / "img_comparison").mkdir(exist_ok=True)
        screenshot_comparison_dir = str(Path(Path(image_output_dir) / "img_comparison"))

        # create selected image directory and define it as variable
        Path(Path(image_output_dir) / "img_selected").mkdir(exist_ok=True)

        # create sync image directory and define it as variable
        Path(Path(image_output_dir) / "img_sync").mkdir(exist_ok=True)
        screenshot_sync_dir = str(Path(Path(image_output_dir) / "img_sync"))

        # create sub directories
        Path(Path(image_output_dir) / "img_sync/sync1").mkdir(exist_ok=True)
        Path(Path(image_output_dir) / "img_sync/sync2").mkdir(exist_ok=True)

        print("Folder creation completed", flush=True)

        return screenshot_comparison_dir, screenshot_sync_dir

    def get_b_frames(self, num_source_frames):
        print(
            f"\nGenerating {self.comparison_count} 'B' frames for " "comparison images",
            flush=True,
        )

        b_frames = list(
            linspace(
                int(num_source_frames * 0.15),
                int(num_source_frames * 0.75),
                int(self.comparison_count),
            ).astype(int)
        )

        try:
            for i, frame in enumerate(b_frames):
                while (
                    self.encode_node.get_frame(frame).props["_PictType"].decode() != "B"
                ):
                    frame += 1
                b_frames[i] = frame
        except ValueError:
            raise FrameForgeError(
                "Error! Your encode file is likely an incomplete or corrupted encode"
            )

        print(f"Finished generating {self.comparison_count} 'B' frames", flush=True)

        return b_frames

    def check_de_interlaced(self, num_source_frames, num_encode_frames):
        print("\nChecking if encode has been de-interlaced", flush=True)
        try:
            source_fps = float(self.source_node.fps)
            encode_fps = float(self.encode_node.fps)

            if source_fps != encode_fps:
                if num_source_frames == num_encode_frames:
                    self.source_node = self.core.std.AssumeFPS(
                        self.source_node,
                        fpsnum=self.encode_node.fps.numerator,
                        fpsden=self.encode_node.fps.denominator,
                    )
                    print(
                        "Adjusting source fps to match the encode using AssumeFPS() on the source",
                        flush=True,
                    )
                else:
                    even_frames_for = ""
                    if num_source_frames != num_encode_frames:
                        file_differences = float(num_source_frames / num_encode_frames)
                        if file_differences > 1.01:
                            even_frames_for = "source"
                            self.source_node = self.core.std.SelectEvery(
                                self.source_node, cycle=2, offsets=0
                            )
                        elif file_differences < 0.99:
                            even_frames_for = "encode"
                            self.encode_node = self.core.std.SelectEvery(
                                self.encode_node, cycle=2, offsets=0
                            )
                        print(
                            f"Source: FPS={source_fps} Frames={num_source_frames}\n"
                            f"Encode: FPS={encode_fps} Frames={num_encode_frames}\n"
                            "Source vs Encode appears to be different, we're going to assume encode has been"
                            f" de-interlaced, automatically generating even frames for {even_frames_for}",
                            flush=True,
                        )
            else:
                print("No de-interlacing detected", flush=True)
        except ValueError:
            print(
                "There was an error while detecting source or encode fps, attempting to continue",
                flush=True,
            )

    def index_lsmash(self):
        print("Indexing source", flush=True)

        # index source file
        # if index is found in the StaxRip temp working directory, attempt to use it
        if (
            Path(str(Path(self.source_file).with_suffix("")) + "_temp/").is_dir()
            and Path(
                str(Path(self.source_file).with_suffix("")) + "_temp/temp.lwi"
            ).is_file()
        ):
            print("Index found in StaxRip temp, attempting to use", flush=True)

            # define cache path
            lwi_cache_path = Path(
                str(Path(self.source_file).with_suffix("")) + "_temp/temp.lwi"
            )

            # try to use index on source file with the cache path
            try:
                self.source_node = self.core.lsmas.LWLibavSource(
                    source=self.source_file, cachefile=lwi_cache_path
                )
                self.reference_source_file = self.core.lsmas.LWLibavSource(
                    source=self.source_file, cachefile=lwi_cache_path
                )
                print("Using existing index", flush=True)
            # if index cannot be used
            except vs.Error:
                print("L-Smash version miss-match, indexing source again", flush=True)

                # index source file
                self.source_node = self.core.lsmas.LWLibavSource(self.source_file)
                self.reference_source_file = self.core.lsmas.LWLibavSource(
                    self.source_file
                )

        # if no existing index is found index source file
        else:
            cache_path = Path(Path(self.source_file).with_suffix(".lwi"))
            try:
                # create index
                self.source_node = self.core.lsmas.LWLibavSource(
                    self.source_file, cachefile=cache_path
                )
                self.reference_source_file = self.core.lsmas.LWLibavSource(
                    self.source_file, cachefile=cache_path
                )
            except vs.Error:
                # delete index
                Path(self.source_file).with_suffix(".lwi").unlink(missing_ok=True)
                # create index
                self.source_node = self.core.lsmas.LWLibavSource(
                    self.source_file, cachefile=cache_path
                )
                self.reference_source_file = self.core.lsmas.LWLibavSource(
                    self.source_file, cachefile=cache_path
                )

        print("Source index completed\n\nIndexing encode", flush=True)

        # define a path for encode index to go
        if self.index_dir:
            index_base_path = Path(self.index_dir) / Path(self.encode_file).name
            cache_path_enc = index_base_path.with_suffix(".lwi")
        else:
            cache_path_enc = Path(Path(self.encode_file).with_suffix(".lwi"))

        try:
            # create index
            self.encode_node = self.core.lsmas.LWLibavSource(
                self.encode_file, cachefile=cache_path_enc
            )
        except vs.Error:
            # delete index
            cache_path_enc.unlink(missing_ok=True)
            # create index
            self.encode_node = self.core.lsmas.LWLibavSource(
                self.encode_file, cachefile=cache_path_enc
            )

        print("Encode index completed", flush=True)

    def index_ffms2(self):
        print("Indexing source", flush=True)

        # index source file
        # if index is found in the StaxRip temp working directory, attempt to use it
        if (
            Path(str(Path(self.source_file).with_suffix("")) + "_temp/").is_dir()
            and Path(
                str(Path(self.source_file).with_suffix("")) + "_temp/temp.ffindex"
            ).is_file()
        ):
            print("Index found in StaxRip temp, attempting to use", flush=True)

            # define cache path
            ffindex_cache_path = Path(
                str(Path(self.source_file).with_suffix("")) + "_temp/temp.ffindex"
            )

            # try to use index on source file with the cache path
            try:
                self.source_node = self.core.ffms2.Source(
                    source=self.source_file, cachefile=ffindex_cache_path
                )
                self.reference_source_file = self.core.ffms2.Source(
                    source=self.source_file, cachefile=ffindex_cache_path
                )
                print("Using existing index", flush=True)
            # if index cannot be used
            except vs.Error:
                print("FFMS2 version miss-match, indexing source again", flush=True)

                # index source file
                self.source_node = self.core.ffms2.Source(self.source_file)
                self.reference_source_file = self.core.ffms2.Source(self.source_file)

        # if no existing index is found index source file
        else:
            try:
                # create index
                print(
                    "FFMS2 library doesn't allow progress, please wait while the index is completed",
                    flush=True,
                )
                self.source_node = self.core.ffms2.Source(self.source_file)
                self.reference_source_file = self.core.ffms2.Source(self.source_file)
            except vs.Error:
                # delete index
                Path(self.source_file).with_suffix(".ffindex").unlink(missing_ok=True)
                # create index
                print(
                    "FFMS2 library doesn't allow progress, please wait while the index is completed",
                    flush=True,
                )
                self.source_node = self.core.ffms2.Source(self.source_file)
                self.reference_source_file = self.core.ffms2.Source(self.source_file)

        print("Source index completed\n\nIndexing encode", flush=True)

        # define a path for encode index to go
        if self.index_dir:
            index_base_path = Path(self.index_dir) / Path(self.encode_file).name
            cache_path_enc = Path(str(index_base_path) + ".ffindex")
        else:
            cache_path_enc = Path(self.encode_file + ".ffindex")

        try:
            self.encode_node = self.core.ffms2.Source(
                self.encode_file, cachefile=cache_path_enc
            )
        except vs.Error:
            cache_path_enc.unlink(missing_ok=True)
            self.encode_node = self.core.ffms2.Source(
                self.encode_file, cachefile=cache_path_enc
            )

        print("Encode index completed", flush=True)

    def load_plugins(self):
        plugin_path = get_working_dir() / "img_plugins"
        if not plugin_path.is_dir() and not plugin_path.exists():
            raise FrameForgeError("Can not detect plugin directory")
        else:
            for plugin in plugin_path.glob("*.dll"):
                self.core.std.LoadPlugin(Path(plugin).resolve())
