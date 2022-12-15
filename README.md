# rm-trash

rm-trash is a macOS command-line utility that moves files and directories to the Trash.
Unlike [similar](https://github.com/ali-rantakari/trash) [tools](https://github.com/sindresorhus/macos-trash),
rm-trash intends to be a complete alternative to `rm` and `rmdir`, to the extent that you could use aliases
to have rm-trash replace them both.

rm-trash works by communicating with Finder
through [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html),
so it's no different from moving files to the Trash
from within Finder itself.

## Installation

Install rm-trash with [Homebrew](https://brew.sh) via
the [Houkago Tea Tap](https://github.com/celsiusnarhwal/homebrew-htt).

```bash
brew tap celsiusnarhwal/htt
brew install rm-trash
```

## Usage

Invoke rm-trash with the `trash` command, which will become available after installation.

```bash
trash --help
```

will tell you everything you need to know.

## Replacing `rm` and `rmdir`

If you wish, you can replace `rm` and `rmdir` with aliases to `trash`.

```bash
alias rm="trash trash"
alias rmdir="trash dir"
```

`trash` supports all options of both commands. Run `trash --help` for details.

## Limitations

rm-trash refuses to as root when [System Integrity Protection](https://support.apple.com/en-us/HT204899) (SIP) is disabled.
You can still run rm-trash as a non-root user when SIP is disabled, or as any user when SIP is enabled. This limitation
is intended to prevent you from accidentally trashing files and directories that are typically protected by SIP.

If you must remove files as root while SIP is disabled, you can always fall back to `rm`.

## License

rm-trash is licensed under the [MIT License](LICENSE.md).