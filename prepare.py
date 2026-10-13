#!/usr/bin/env python3
"""Reassemble and verify this offline Godot checkpoint (Python 3.8+)."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import zipfile

CHUNK_SIZE = 196608
ROOT = Path(__file__).absolute().parent


def fail(message):
    raise ValueError(message)


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value:
        fail("Invalid relative path: %r" % value)
    parts = value.split("/")
    for part in parts:
        if (not part or part in (".", "..") or part[-1:] in (".", " ")
                or any(ord(c) < 32 or c in '<>:"|?*' for c in part)
                or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", part, re.I)):
            fail("Unsafe or nonportable path: %r" % value)
    if PurePosixPath(value).is_absolute():
        fail("Absolute paths are not allowed")
    return parts


def no_links(path):
    """Reject existing symlinks and Windows junction/reparse points, including ancestors."""
    path = Path(os.path.abspath(str(path)))
    for item in reversed((path,) + tuple(path.parents)):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 0x400):
            fail("Symlink/reparse-point path is not allowed: %s" % item)


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def check_file(path, record):
    no_links(path)
    if not path.is_file() or path.stat().st_size != record["size"] or digest(path) != record["sha256"]:
        fail("Missing, changed, or corrupt file: %s" % path)


def validate_manifest(manifest):
    if (manifest.get("version") != 1
            or not re.fullmatch(r"[0-9a-f]{64}", manifest.get("archive_sha256", ""))
            or not isinstance(manifest.get("archive_size"), int) or manifest["archive_size"] <= 0):
        fail("Invalid manifest version, archive size, or SHA-256")
    files, parts = manifest.get("files"), manifest.get("parts")
    if not isinstance(files, list) or not files or not isinstance(parts, list) or not parts:
        fail("Invalid manifest file/part count")
    seen = set()
    for item in files:
        safe_relative(item["path"])
        name = item["path"].casefold()
        if name in seen:
            fail("Duplicate/case-colliding manifest path: " + item["path"])
        seen.add(name)
        if item.get("mode") not in ("100644", "100755"):
            fail("Only regular files are supported")
    for name in seen:
        if any("/".join(name.split("/")[:i]) in seen for i in range(1, len(name.split("/")))):
            fail("File/directory collision in manifest")
    for index, item in enumerate(parts):
        if item["name"] != "assets.part%04d" % index:
            fail("Missing, duplicate, or out-of-order chunk")
        if not (0 < item["size"] <= CHUNK_SIZE) or (index < len(parts) - 1 and item["size"] != CHUNK_SIZE):
            fail("Invalid chunk size")
    for item in files + parts:
        if not isinstance(item["size"], int) or item["size"] < 0 or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            fail("Invalid size or SHA-256 in manifest")
    if sum(item["size"] for item in parts) != manifest.get("archive_size"):
        fail("Archive size does not match chunks")
    return files, parts


def check_destinations(project, files):
    no_links(project)
    if project.exists() and not project.is_dir():
        fail("project exists but is not a directory")
    for item in files:
        target = project.joinpath(*safe_relative(item["path"]))
        no_links(target)
        for parent in target.parents:
            if parent == project.parent:
                break
            if parent.exists() and not parent.is_dir():
                fail("A file blocks a destination directory: %s" % parent)
        if target.exists():
            try:
                check_file(target, item)
            except ValueError:
                fail("Will not overwrite an existing/modified file: %s\nUse a fresh package folder, or back up and move that file yourself." % target)


def main():
    no_links(ROOT)
    transport = ROOT / "transport"
    manifest_path = transport / "manifest.json"
    no_links(manifest_path)
    with manifest_path.open("r", encoding="utf-8-sig") as stream:
        manifest = json.load(stream)
    files, parts = validate_manifest(manifest)
    project = ROOT / "project"
    # Preflight every existing destination before creating project files.
    check_destinations(project, files)
    with tempfile.TemporaryDirectory(prefix=".pelican-prepare-", dir=str(ROOT)) as temporary:
        work = Path(temporary)
        archive_path, staged = work / "assets.zip", work / "project"
        staged.mkdir()
        print("Verifying and joining %d offline chunks..." % len(parts), flush=True)
        with archive_path.open("xb") as output:
            for item in parts:
                source = transport / item["name"]
                no_links(source)
                part_hash, size = hashlib.sha256(), 0
                with source.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        size += len(block)
                        part_hash.update(block)
                        output.write(block)
                if size != item["size"] or part_hash.hexdigest() != item["sha256"]:
                    fail("Corrupt or incomplete chunk: " + item["name"])
        check_file(archive_path, {"size": manifest["archive_size"], "sha256": manifest["archive_sha256"]})
        expected = {item["path"]: item for item in files}
        print("Archive verified. Extracting to a temporary folder...", flush=True)
        with zipfile.ZipFile(archive_path, "r") as archive:
            entries = archive.infolist()
            if len(entries) != len(files):
                fail("ZIP file count differs from manifest")
            seen = set()
            for entry in entries:
                components = safe_relative(entry.filename)
                if entry.filename not in expected or entry.filename in seen or entry.is_dir():
                    fail("Unexpected/duplicate ZIP entry: " + entry.filename)
                seen.add(entry.filename)
                unix_mode = entry.external_attr >> 16
                if stat.S_IFMT(unix_mode) not in (0, stat.S_IFREG):
                    fail("Nonregular ZIP entry: " + entry.filename)
                record = expected[entry.filename]
                if entry.file_size != record["size"]:
                    fail("Unexpected ZIP entry size")
                destination = staged.joinpath(*components)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, destination.open("xb") as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
                check_file(destination, record)
                destination.chmod(0o755 if record["mode"] == "100755" else 0o644)
        if seen != set(expected):
            fail("ZIP is incomplete")
        # Check again after extraction. Open new files exclusively; never replace existing ones.
        check_destinations(project, files)
        print("All %d extracted hashes verified. Preparing project/..." % len(files), flush=True)
        for item in files:
            relative = safe_relative(item["path"])
            target, source = project.joinpath(*relative), staged.joinpath(*relative)
            no_links(target)
            if target.exists():
                check_file(target, item)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            no_links(target.parent)
            created = False
            try:
                with target.open("xb") as output, source.open("rb") as input_stream:
                    created = True
                    shutil.copyfileobj(input_stream, output, 1024 * 1024)
                target.chmod(0o755 if item["mode"] == "100755" else 0o644)
                check_file(target, item)
            except Exception:
                if created:
                    target.unlink()
                raise
        for item in files:
            check_file(project.joinpath(*safe_relative(item["path"])), item)
    print("SUCCESS: all %d project files match the checkpoint." % len(files))
    print("Open project/project.godot with Godot 4.6.3 Standard, wait for import, then press F5.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("PREPARATION FAILED: %s" % error, file=sys.stderr)
        sys.exit(1)
