#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import get_default_avd, set_default_avd, load_config

app = typer.Typer()
console = Console()


def detect_sdk_path() -> Path:
    env_sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if env_sdk:
        sdk = Path(env_sdk).expanduser()
        if sdk.exists():
            return sdk
    default_mac = Path.home() / "Library/Android/sdk"
    if default_mac.exists():
        return default_mac
    raise RuntimeError("Android SDK not found. Run 'avd setup' first.")


def run_bash(cmd: str, check: bool = True):
    subprocess.run(["bash", "-c", cmd], check=check, text=True)


@app.command()
def setup(
        avd_name: str = "HomeMonitor",
        android_version: str = "34",
):
    """1️⃣ Full setup: installs tools + creates default AVD."""

    config = load_config()
    if config.get("setup_complete"):
        console.print("✅ Already setup! Run 'avd start'", style="green")
        raise typer.Exit()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task1 = progress.add_task("Installing Homebrew...", total=None)
        if not any(Path(p).exists() for p in ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]):
            run_bash(
                '''/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"''')
        progress.remove_task(task1)

        task2 = progress.add_task("Installing Python tools...", total=None)
        run_bash("brew install python@3.12")
        run_bash("pip3 install -e .")
        progress.remove_task(task2)

        task3 = progress.add_task("Installing Android SDK...", total=None)
        run_bash("brew install --cask android-commandlinetools")
        sdkmanager = detect_sdk_path() / "cmdline-tools/latest/bin/sdkmanager"
        run_bash(f'"{sdkmanager}" --licenses', check=False)
        run_bash(
            f'"{sdkmanager}" "platforms;android-{android_version}" "emulator" "platform-images;android-{android_version};google_apis;x86_64"')
        progress.remove_task(task3)

        task4 = progress.add_task(f"Creating AVD '{avd_name}'...", total=None)
        avdmanager = detect_sdk_path() / "cmdline-tools/latest/bin/avdmanager"
        run_bash(
            f'"{avdmanager}" create avd -n {avd_name} -k "system-images;android-{android_version};google_apis;x86_64" -d pixel_6')
        set_default_avd(avd_name)
        progress.remove_task(task4)

    config["setup_complete"] = True
    config["avd_name"] = avd_name
    from .config import save_config
    save_config(config)

    console.print(f"\n✅ Setup complete! Default AVD: {avd_name}", style="green")
    console.print("💡 Install monitoring apps via Play Store in emulator")
    console.print("🚀 Next: 'avd start'")


@app.command()
def start(
        avd_name: Optional[str] = None,
        headless: bool = typer.Option(False, "--headless"),
):
    """2️⃣ Start default AVD in background (prompts setup if needed)."""

    if not avd_name:
        default = get_default_avd()
        if not default:
            console.print("❌ No default AVD found. Run 'avd setup' first!", style="red")
            raise typer.Exit(1)
        avd_name = default
        console.print(f"🌟 Using default AVD: {avd_name}")

    sdk = detect_sdk_path()
    emu = sdk / "emulator" / "emulator"

    if not emu.exists():
        console.print("❌ Emulator not found. Run 'avd setup' first!", style="red")
        raise typer.Exit(1)

    cmd = [str(emu), "-avd", avd_name, "-no-boot-anim", "-no-snapshot-save"]
    if headless:
        cmd.extend(["-no-window", "-no-audio"])

    console.print(f"🚀 Starting {avd_name} in background...", style="green")
    console.print(f"   {' '.join(cmd)}")
    subprocess.Popen(cmd)
    console.print("✅ Emulator started! Check with 'avd status'", style="green")


@app.command()
def status():
    """Check if emulator is running."""
    sdk = detect_sdk_path()
    result = subprocess.run([str(sdk / "emulator" / "emulator"), "-list-avds"],
                            capture_output=True, text=True)
    console.print("Available AVDs:")
    console.print(result.stdout)


if __name__ == "__main__":
    app()
