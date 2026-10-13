# Windows local test · interim build

This is the 2026-10-13 work-in-progress checkpoint, prepared for local testing while further art work continues. It is not the final visual-quality milestone.

## Get the project

If Git is already installed, open a terminal in your chosen folder and run:

```powershell
git clone https://github.com/yunmeze/Tihu.git
```

Alternatively, use **Code → Download ZIP** on the repository page and extract the ZIP before opening the project.

## Open and run

1. Download **Godot 4.6.3 Standard** for your Windows architecture from the [official version archive](https://godotengine.org/download/archive/4.6.3-stable/). This GDScript project does not require the .NET build.
2. Extract and launch Godot. In its project manager, choose **Import** and select this repository's `project.godot`.
3. Open the project and wait until its first model/texture import finishes. The `.godot` folder is a local cache that Godot regenerates; it is deliberately not committed.
4. Press **F5** to run the configured main scene. No export templates or Blender installation are required for this step.

The project declares Godot 4.6 / GL Compatibility and was tested using 4.6.3. Other versions have not been verified.

## Quick test

- The initial view is portrait camera 3. Press 1 or 2 for the postcard/follow views.
- Space pauses/resumes the rider, wheels, water and vegetation.
- Up/Down or +/− changes the riding pace.
- Drag to orbit within the presentation area; scroll for bounded zoom.
- R resets. The bottom control strip is clickable.
- F12 writes a native viewport PNG to `captures/`.

The scene is a compact interactive ride loop with no audio. It is not a navigable open world or physical bicycle simulator.

## If playback is slow

The verification host uses CPU software rendering (Mesa llvmpipe). Its recorded FPS does **not** establish the FPS of your GPU. Measure actual playback on your machine.

A lower-cost preview preserves the scene art and reduces antialiasing/shadow/window cost. From a terminal with Godot on PATH, run:

```powershell
godot --path . -- --software-preview --compact-preview
```

If Godot is not on PATH, use the full path to its executable instead. Run the command from the repository folder. This mode uses FXAA, 2048 shadows and a 960×600 window; the default is higher quality.

See [verification details](VERIFICATION.md) for limits. The included `captures/native_preview.mp4` is an offline native Movie Maker render; its 30 FPS cadence is not a real-time speed claim.

## Editable source

`source/pelican_coast.blend` contains the editable authored models. Runtime uses the committed GLB files, textures, fonts, GDScript and shaders. To re-export models, follow [the source workflow](../source/ASSET_WORKFLOW.md). Existing texture/font provenance and licenses are included.
