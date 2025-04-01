# Changelog

All notable changes to this project will be documented in this file starting with **1.3.6**.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-4-01

### Added

- New arg **--source-sub-title**, to define the **Source** image subtitles (defaults to 'Source').
- New arg **--fpng-compression**, this allows control over fpng's compression level (defaults to 1 - slow compression).
- New arg **--sub-font-name**, this allows control of subtitle font names (defaults to Segoe UI).
- New arg **--sub-secondary-color**, this allows control of the secondary subtitle color.
- New arg **--sub-outline-color**, this allows control of the outline subtitle color.
- New arg **--sub-back-color**, this allows control of the back subtitle color.
- New args **--sub-bold**, **--sub-italic**, **--sub-underline**, and **--sub-strikeout** this allows control of several styles (bold defaults to 1).
- New args **--sub-scale-x** and **--sub-scale-y** this allows control of subtitle scaling (defaults to 100).
- New arg **--sub-spacing**, this allows control of the subtitle spacing (defaults to 0).
- New arg **--sub-border-style**, this allows control of the subtitle spacing (defaults to 0).
- New arg **--sub-outline-width**, this allows control of the subtitle outline width (defaults to 1).
- New arg **--sub-shadow-depth**, this allows control of the subtitle shadow depth (defaults to 0).
- New args **--sub-left-margin**, **--sub-right-margin**, and **--sub-vertical-margin**, this allows control of several margins (they all default to 10).
- New arg **--start-trim**, this allows control of the starting percentage to generate images from (defaults to 12%).
- New arg **--end-trim**, this allows control of the ending percentage to generate images from (defaults to 12%).
- Moving images now warns/gives the user a chance to close folders/files/terminals related to the path of the image output via a message/timer in an attempt to avoid failure.
- Now catches **KeyboardInterrupt** and properly exits/cleans up.

### Changed

- **--release-sub-title** now defaults to 'Encode'.
- **--release-sub-title** is set to be deprecated, replaced with **--encode-sub-title**. You will get a warning if you use **--release-sub-title** until the next version.
- Improve description for alignment.
- Massively improved **b-frame** detection logic for the **encode** images. It now can handle _smaller_ files by utilizing a **fallback** mode that will find **I**, **P**, and **B** frames if there isn't enough **b-frames** in a media file.
- **B-frame** detection now **randomly** does a small offset to generate **unique** images on the same film when ran multiple times.
- **B-frame** detection is now **async** detecting things in batches of 5, this can massively speed up the detection around **40x** depending on drive speed.

### Fixed

- Potential issue with an unbound error.
- Some minor code issues and type hinting.
