"""Build the private, offline migration bundle from the local installed skill snapshots."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
WORKFLOW = HERE / "short-drama-episode-workflow"
DEPENDENCIES = (
    "byted-ind-ecom-prompt-to-video", "hyperframes", "hyperframes-cli", "hyperframes-registry",
    "media-use", "remotion-best-practices", "video-use", "short-drama", "short-drama-write",
    "short-drama-assets", "short-drama-image-prompts", "short-drama-storyboard",
    "short-drama-video-prompts", "short-drama-produce", "short-drama-edit", "short-drama-review",
    "free-bgm-search",
)
TARGETS = [(system, arch) for system in ("darwin", "linux", "windows") for arch in ("amd64", "arm64")]
SKIP = {".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
        ".git", ".hg", ".svn", ".DS_Store", ".env", ".envrc", ".npmrc"}
ARCHIVE = "assets/skill-dependencies.zip"
MANIFEST = "assets/portable-manifest.json"


def members(folder):
    for directory, children, names in os.walk(folder):
        children[:] = sorted(c for c in children if c not in SKIP and not c.startswith("."))
        for name in sorted(names):
            if name in SKIP or (name.startswith(".") and name != ".env.example"):
                continue
            path = Path(directory) / name
            if path.suffix.lower() in {".pyc", ".pyo", ".pem", ".p12", ".key", ".pfx"}:
                continue
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Unexpected non-regular package member: {path}")
            yield path


def add(archive, src, name):
    mode = 0o755 if src.stat().st_mode & 0o111 else 0o644
    info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, src.read_bytes())


def build():
    installed = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "skills"
    if not all((installed / name / "SKILL.md").is_file() for name in DEPENDENCIES):
        raise RuntimeError("One or more installed source skills are missing")
    programs = WORKFLOW / "scripts/bin"
    programs.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        def compile_target(target):
            system, arch = target
            name = f"{system}-{arch}" + (".exe" if system == "windows" else "")
            env = os.environ | {"GOOS": system, "GOARCH": arch, "CGO_ENABLED": "0",
                                "GOCACHE": str(Path(temp) / "go-cache"), "GOTOOLCHAIN": "local"}
            subprocess.run(["go", "build", "-p=3", "-trimpath", "-buildvcs=false", "-ldflags=-s -w",
                            "-o", str(programs / name), str(WORKFLOW / "scripts/install_portable.go")],
                           env=env, check=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(compile_target, TARGETS))
    with zipfile.ZipFile(WORKFLOW / ARCHIVE, "w") as archive:
        for name in DEPENDENCIES:
            for path in members(installed / name):
                add(archive, path, path.relative_to(installed).as_posix())
    workflow_files = [p.relative_to(WORKFLOW).as_posix() for p in members(WORKFLOW)]
    lock = {"archive_sha256": hashlib.sha256((WORKFLOW / ARCHIVE).read_bytes()).hexdigest(),
            "skills": list(DEPENDENCIES), "workflow_files": sorted(set(workflow_files) - {MANIFEST, ARCHIVE})}
    (WORKFLOW / MANIFEST).write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    output = HERE / "short-drama-episode-workflow-portable.zip"
    with tempfile.NamedTemporaryFile(dir=HERE, delete=False) as file:
        staging = Path(file.name)
    try:
        with zipfile.ZipFile(staging, "w") as archive:
            for p in members(WORKFLOW):
                add(archive, p, p.relative_to(HERE).as_posix())
        staging.replace(output)
    finally:
        staging.unlink(missing_ok=True)
    print(output, output.stat().st_size, "bytes")


if __name__ == "__main__":
    build()
