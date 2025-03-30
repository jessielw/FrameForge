import re
import shutil
import tempfile
from random import choice
from pathlib import Path
from typing import Tuple
from numpy import linspace

import vapoursynth as vs
from awsmfunc import ScreenGenEncoder, ScreenGen, FrameInfo, DynamicTonemap
from frame_forge.exceptions import FrameForgeError
from frame_forge.utils import get_working_dir, hex_to_bgr


class GenerateImages:
    def __init__(
        self,
        source_file: Path,
        encode_file: Path,
        fpng_compression: int,
        frames: str,
        image_dir: Path,
        indexer: str,
        img_lib: str,
        source_index_path: None | str,
        encode_index_path: None | str,
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
        sub_size: int,
        sub_alignment: int,
        sub_color: str,
        sub_secondary_color: str,
        sub_outline_color: str,
        sub_back_color: str,
        sub_font_name: str,
        sub_bold: int,
        sub_italic: int,
        sub_underline: int,
        sub_strikeout: int,
        sub_scale_x: int,
        sub_scale_y: int,
        sub_spacing: int,
        sub_border_style: int,
        sub_outline_width: int,
        sub_shadow_depth: int,
        sub_left_margin: int,
        sub_right_margin: int,
        sub_vertical_margin: int,
        source_sub_title: str,
        release_sub_title: str,
    ):
        self.source_file = source_file
        self.source_node = None
        self.reference_source_file = None
        self.encode_file = encode_file
        self.fpng_compression = fpng_compression
        self.frames = frames
        self.encode_node = None
        self.image_dir = image_dir
        self.indexer = indexer
        self.img_lib = ScreenGenEncoder(img_lib)
        self.source_index_path = source_index_path
        self.encode_index_path = encode_index_path
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
        self.sub_size = sub_size
        self.sub_alignment = sub_alignment
        self.sub_color = sub_color
        self.sub_secondary_color = sub_secondary_color
        self.sub_outline_color = sub_outline_color
        self.sub_back_color = sub_back_color
        self.sub_font_name = sub_font_name
        self.sub_bold = sub_bold
        self.sub_italic = sub_italic
        self.sub_underline = sub_underline
        self.sub_strikeout = sub_strikeout
        self.sub_scale_x = sub_scale_x
        self.sub_scale_y = sub_scale_y
        self.sub_spacing = sub_spacing
        self.sub_border_style = sub_border_style
        self.sub_outline_width = sub_outline_width
        self.sub_shadow_depth = sub_shadow_depth
        self.sub_left_margin = sub_left_margin
        self.sub_right_margin = sub_right_margin
        self.sub_vertical_margin = sub_vertical_margin
        self.source_sub_title = source_sub_title
        self.release_sub_title = release_sub_title

        self.core = vs.core
        self.load_plugins()

        self.temp_dir: Path = None

    def process_images(self) -> Path:
        self.check_index_paths()

        if self.indexer == "lsmash":
            self.index_lsmash()

        elif self.indexer == "ffms2":
            self.index_ffms2()

        num_source_frames = len(self.source_node)
        num_encode_frames = len(self.encode_node)

        # ASS subtitle styles
        # Font Name, Font Size, Primary Color, Secondary Color, Outline Color, Back Color, Bold,
        # Italic, Underline, Strikeout, Scale X, Scale Y, Spacing, Angle, Border Style, Outline Width,
        # Shadow Depth, Alignment, Left Margin, Right Margin, Vertical Margin, Encoding

        # bgr color
        color = "&H14FF39"
        if self.sub_color:
            color = hex_to_bgr(self.sub_color)

        secondary_color = "&H00000000"
        if self.sub_secondary_color:
            secondary_color = hex_to_bgr(self.sub_secondary_color)

        outline_color = "&H00000000"
        if self.sub_outline_color:
            outline_color = hex_to_bgr(self.sub_outline_color)

        back_color = "&H00000000"
        if self.sub_back_color:
            back_color = hex_to_bgr(self.sub_back_color)

        selected_sub_style = (
            f"{self.sub_font_name},{self.sub_size},{color},{secondary_color},{outline_color},{back_color},"
            f"{self.sub_bold},{self.sub_italic},{self.sub_underline},{self.sub_strikeout},"
            f"{self.sub_scale_x},{self.sub_scale_y},{self.sub_spacing},0,{self.sub_border_style},"
            f"{self.sub_outline_width},{self.sub_shadow_depth},{self.sub_alignment},{self.sub_left_margin},"
            f"{self.sub_right_margin},{self.sub_vertical_margin},1"
        )
        sync_sub_base = (
            "Segoe UI,{size},&H31FF31&,&H00000000,&H00000000,&H00000000,"
            "1,0,0,0,100,100,0,0,1,1,0,{pos},10,10,10,1"
        )
        selected_sub_style_ref = sync_sub_base.format(
            size=str(self.sub_size + 5), pos="7"
        )
        selected_sub_style_sync = sync_sub_base.format(
            size=str(self.sub_size + 5), pos="9"
        )

        self.check_de_interlaced(num_source_frames, num_encode_frames)

        b_frames = None
        if not self.frames:
            b_frames = self.get_b_frames(num_source_frames)

        (
            temp_screenshot_comparison_dir,
            temp_selected_dir,
            temp_screenshot_sync_dir,
        ) = self.generate_temp_folders()

        self.handle_crop()

        self.handle_resize()

        self.handle_hdr()

        vs_source_info, vs_encode_info = self.handle_subtitles(selected_sub_style)

        if not self.frames:
            self.generate_screens(
                b_frames,
                vs_source_info,
                vs_encode_info,
                temp_screenshot_comparison_dir,
                temp_screenshot_sync_dir,
                selected_sub_style_ref,
                selected_sub_style_sync,
            )
        else:
            self.generate_exact_screens(
                vs_source_info,
                vs_encode_info,
                temp_screenshot_comparison_dir,
            )

        final_folder = self.generate_final_folder()
        self.move_images(temp_screenshot_comparison_dir.parent, final_folder)
        self.clean_temp()

        return final_folder

    @staticmethod
    def screen_gen_callback(sg_call_back):
        print(
            str(sg_call_back).replace("ScreenGen: ", "").replace("\n", "").strip(),
            flush=True,
        )

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
            ScreenGen(
                vs_encode_ref_info,
                frame_numbers=[ref_frame],
                fpng_compression=self.fpng_compression,
                folder=screenshot_sync_dir,
                suffix="b_encode__%d",
                callback=self.screen_gen_callback,
                encoder=self.img_lib,
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
            ScreenGen(
                vs_sync_info,
                frame_numbers=[sync_frame],
                fpng_compression=self.fpng_compression,
                folder=Path(screenshot_sync_dir),
                suffix="a_source__%d",
                callback=self.screen_gen_callback,
                encoder=self.img_lib,
            )

    def generate_exact_screens(
        self,
        vs_source_info,
        vs_encode_info,
        screenshot_comparison_dir,
    ) -> Path:
        print("\nGenerating screenshots, please wait", flush=True)

        # generate source images
        ScreenGen(
            vs_source_info,
            frame_numbers=[
                self.frames[i] for i in range(len(self.frames)) if i % 2 == 0
            ],
            fpng_compression=self.fpng_compression,
            folder=screenshot_comparison_dir,
            suffix="a_source__%d",
            callback=self.screen_gen_callback,
            encoder=self.img_lib,
        )

        # generate encode images
        ScreenGen(
            vs_encode_info,
            frame_numbers=[
                self.frames[i] for i in range(len(self.frames)) if i % 2 != 0
            ],
            fpng_compression=self.fpng_compression,
            folder=screenshot_comparison_dir,
            suffix="b_encode__%d",
            callback=self.screen_gen_callback,
            encoder=self.img_lib,
        )

        print("Screen generation completed", flush=True)
        return screenshot_comparison_dir

    def generate_screens(
        self,
        b_frames,
        vs_source_info,
        vs_encode_info,
        screenshot_comparison_dir,
        screenshot_sync_dir,
        selected_sub_style_ref,
        selected_sub_style_sync,
    ) -> Path:
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
        ScreenGen(
            vs_source_info,
            frame_numbers=sync_frames,
            fpng_compression=self.fpng_compression,
            folder=screenshot_comparison_dir,
            suffix="a_source__%d",
            callback=self.screen_gen_callback,
            encoder=self.img_lib,
        )

        # generate encode images
        ScreenGen(
            vs_encode_info,
            frame_numbers=b_frames,
            fpng_compression=self.fpng_compression,
            folder=screenshot_comparison_dir,
            suffix="b_encode__%d",
            callback=self.screen_gen_callback,
            encoder=self.img_lib,
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
        return screenshot_comparison_dir

    def handle_subtitles(self, selected_sub_style):
        vs_source_info = self.core.sub.Subtitle(
            clip=self.source_node, text=self.source_sub_title, style=selected_sub_style
        )
        vs_encode_info = FrameInfo(
            clip=self.encode_node,
            title=self.release_sub_title,
            style=selected_sub_style,
        )

        return vs_source_info, vs_encode_info

    def handle_hdr(self):
        if self.tone_map:
            self.source_node = DynamicTonemap(clip=self.source_node, libplacebo=False)
            self.encode_node = DynamicTonemap(
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

    def generate_final_folder(self) -> Path:
        print("\nCreating final output folder", flush=True)
        if self.image_dir:
            image_output_dir = Path(self.image_dir)
        else:
            image_output_dir = Path(
                Path(self.encode_file).parent / f"{Path(self.encode_file).stem}_images"
            )

        if image_output_dir.exists():
            for folder in ("img_comparison", "img_selected", "img_sync"):
                rm_path = image_output_dir / folder
                if rm_path.is_dir() and rm_path.exists():
                    shutil.rmtree(rm_path, ignore_errors=True)

        image_output_dir.mkdir(exist_ok=True, parents=True)

        print("Folder creation completed", flush=True)

        return image_output_dir

    def generate_temp_folders(self) -> Tuple[Path, Path, Path]:
        print("\nCreating temporary folders for images", flush=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ff_"))

        screenshot_comparison_dir = Path(Path(self.temp_dir) / "img_comparison")
        screenshot_comparison_dir.mkdir(exist_ok=True)

        selected_dir = Path(Path(self.temp_dir) / "img_selected")
        selected_dir.mkdir(exist_ok=True)

        screenshot_sync_dir = Path(Path(self.temp_dir) / "img_sync")
        screenshot_sync_dir.mkdir(exist_ok=True)

        Path(screenshot_sync_dir / "sync1").mkdir(exist_ok=True)
        Path(screenshot_sync_dir / "sync2").mkdir(exist_ok=True)

        print("Folder creation completed", flush=True)

        return screenshot_comparison_dir, selected_dir, screenshot_sync_dir

    def move_images(self, temp_folder: Path, output_folder: Path) -> None:
        print("\nMoving generated images")

        for sub_folder in temp_folder.iterdir():
            if sub_folder.is_dir():
                target_sub_folder = output_folder / sub_folder.name
                target_sub_folder.mkdir(parents=True, exist_ok=True)

                for item in sub_folder.iterdir():
                    target_item = target_sub_folder / item.name
                    if item.is_dir():
                        shutil.move(item, target_item)
                    else:
                        shutil.move(item, target_sub_folder)

        print("Image move completed", flush=True)

    def clean_temp(self, status: bool = True) -> None:
        if status:
            print("\nRemoving temp folder")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if status:
            print("Temp folder removal completed")

    def get_b_frames(self, num_source_frames):
        print(
            f"\nGenerating {self.comparison_count} 'B' frames for comparison images",
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
            pict_types = ("B", b"B")
            for i, frame in enumerate(b_frames):
                while (
                    self.encode_node.get_frame(frame).props["_PictType"]
                    not in pict_types
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

    def _index_source_lsmash(self):
        print("Indexing source", flush=True)

        # if index is found in the StaxRip temp working directory, attempt to use it
        src_file_path = Path(self.source_file)
        tmp_dir = src_file_path.parent / f"{src_file_path.stem}_temp"
        tmp_dir_2 = src_file_path.parent / f"{src_file_path.name}_temp"

        lwi_cache_path = None

        for dir_path in (tmp_dir, tmp_dir_2):
            index_path = dir_path / "temp.lwi"
            if index_path.exists():
                print("Index found in StaxRip temp, attempting to use", flush=True)
                lwi_cache_path = index_path
                break

        if not lwi_cache_path and self.source_index_path.exists():
            print("Index found, attempting to use", flush=True)
            lwi_cache_path = self.source_index_path

        # if no existing index is found index source file
        elif not lwi_cache_path:
            lwi_cache_path = Path(Path(self.source_file).with_suffix(".lwi"))

        try:
            self.source_node = self.core.lsmas.LWLibavSource(
                source=self.source_file, cachefile=lwi_cache_path
            )
            self.reference_source_file = self.core.lsmas.LWLibavSource(
                source=self.source_file, cachefile=lwi_cache_path
            )
            print("Using existing index", flush=True)
        except vs.Error:
            print("L-Smash version miss-match, indexing source again", flush=True)
            self.source_node = self.core.lsmas.LWLibavSource(self.source_file)
            self.reference_source_file = self.core.lsmas.LWLibavSource(self.source_file)

        print("Source index completed", flush=True)

    def _index_encode_lsmash(self):
        print("\nIndexing encode", flush=True)

        if self.encode_index_path:
            cache_path_enc = self.encode_index_path
        else:
            cache_path_enc = Path(Path(self.encode_file).with_suffix(".lwi"))

        try:
            self.encode_node = self.core.lsmas.LWLibavSource(
                self.encode_file, cachefile=cache_path_enc
            )
        except vs.Error:
            cache_path_enc.unlink(missing_ok=True)
            self.encode_node = self.core.lsmas.LWLibavSource(
                self.encode_file, cachefile=cache_path_enc
            )

        print("Encode index completed", flush=True)

    def index_lsmash(self):
        """Index source/encode with lsmash"""

        self._index_source_lsmash()
        self._index_encode_lsmash()

    def _index_source_ffms2(self):
        print("Indexing source", flush=True)

        # if index is found in the StaxRip temp working directory, attempt to use it
        src_file_path = Path(self.source_file)
        tmp_dir = src_file_path.parent / f"{src_file_path.stem}_temp"
        tmp_dir_2 = src_file_path.parent / f"{src_file_path.name}_temp"

        ffindex_cache_path = None

        for dir_path in (tmp_dir, tmp_dir_2):
            index_path = dir_path / "temp.ffindex"
            if index_path.exists():
                print("Index found in StaxRip temp, attempting to use", flush=True)
                ffindex_cache_path = index_path
                break

        if not ffindex_cache_path and self.source_index_path.exists():
            print("Index found, attempting to use", flush=True)
            ffindex_cache_path = self.source_index_path

        # if no existing index is found index source file
        elif not ffindex_cache_path:
            ffindex_cache_path = Path(Path(self.source_file).with_suffix(".ffindex"))
            print(
                "FFMS2 library doesn't allow progress, please wait while the index is completed",
                flush=True,
            )

        try:
            self.source_node = self.core.ffms2.Source(
                self.source_file, cachefile=ffindex_cache_path
            )
            self.reference_source_file = self.core.ffms2.Source(
                self.source_file, cachefile=ffindex_cache_path
            )
        except vs.Error:
            Path(self.source_file).with_suffix(".ffindex").unlink(missing_ok=True)
            print(
                "FFMS2 library doesn't allow progress, please wait while the index is completed",
                flush=True,
            )
            self.source_node = self.core.ffms2.Source(
                self.source_file, cachefile=ffindex_cache_path
            )
            self.reference_source_file = self.core.ffms2.Source(
                self.source_file, cachefile=ffindex_cache_path
            )

        print("Source index completed", flush=True)

    def _index_encode_ffms2(self):
        print("\nIndexing encode", flush=True)

        if self.encode_index_path:
            cache_path_enc = self.encode_index_path
        else:
            cache_path_enc = Path(str(self.encode_file) + ".ffindex")

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

    def index_ffms2(self):
        """Index source/encode with ffms2"""

        self._index_source_ffms2()
        self._index_encode_ffms2()

    def load_plugins(self):
        plugin_path = get_working_dir() / "img_plugins"
        if not plugin_path.is_dir() and not plugin_path.exists():
            raise FrameForgeError("Can not detect plugin directory")
        else:
            for plugin in plugin_path.glob("*.dll"):
                self.core.std.LoadPlugin(Path(plugin).resolve())

    def check_index_paths(self):
        indexer_ext = ".lwi" if self.indexer == "lsmash" else ".ffindex"
        if not self.source_index_path or not Path(self.source_index_path).exists():
            source_path_obj = Path(self.source_file)
            self.source_index_path = source_path_obj.parent / Path(
                f"{source_path_obj.stem}{indexer_ext}"
            )
        else:
            self.source_index_path = Path(self.source_index_path)

        if not self.encode_index_path or not Path(self.encode_index_path).exists():
            encode_path_obj = Path(self.encode_file)
            self.encode_index_path = encode_path_obj.parent / Path(
                f"{encode_path_obj.stem}{indexer_ext}"
            )
        else:
            self.encode_index_path = Path(self.encode_index_path)
