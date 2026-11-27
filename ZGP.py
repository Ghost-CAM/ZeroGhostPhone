#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 PROJECT      : ZERO GHOST MESSAGE ENCRYPTION & DECRYPTION SYSTEM
 MADE BY      : ZERO GHOST TEAM
 DEVELOPED BY : ZERO-X
 FILE         : zero_ghost.py
================================================================================
 MAPPING SOURCE (verbatim from "MessageCipher" in Zero Ghost.py):
     SHIFT              = 7
     Printable ASCII    = 33 - 126  (94 characters)
     Encrypt            : every printable char moves +7 inside the 94-char ring
     Decrypt            : every printable char moves -7 inside the 94-char ring
     Unchanged          : spaces (32), tabs, newlines, non-ASCII characters

 MULTI-LINE INPUT
     Messages can span many lines. Type your text, pressing ENTER after
     each line. To FINISH, press ENTER on 3 consecutive empty lines.
     (Up to 2 empty lines inside a message are kept as part of it.)

 CLIPBOARD SUPPORT
     Termux (Android) : termux-clipboard-set  ->  OSC-52  fallback
     iSH  (iOS)       : pbcopy (if present)   ->  OSC-52  fallback
     Linux / macOS    : wl-copy / xclip / xsel / pbcopy / tkinter
     Windows          : clip.exe  /  tkinter
================================================================================
"""

import os
import sys
import time
import random
import base64
import shutil
import subprocess

# ==============================================================================
# 1. TERMINAL / COLOR LAYER  (ANSI with graceful fallback)
# ==============================================================================

ESC = "\033["
RESET = ESC + "0m"


def _enable_windows_vt():
    """Turn on ANSI escape processing on modern Windows terminals."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


_enable_windows_vt()


def _color_supported():
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False


COLOR_ENABLED = _color_supported()


def _is_tty():
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False


ANIM = COLOR_ENABLED and _is_tty()

# --- palette ---------------------------------------------------------------
GREEN  = "1;92"   # neon green
CYAN   = "1;96"
PURPLE = "1;95"
RED    = "1;91"
BLUE   = "1;94"
YELLOW = "1;93"
WHITE  = "1;97"
DIM    = "2"

PALETTE = [GREEN, CYAN, PURPLE, RED, BLUE, YELLOW]


def paint(text, code=""):
    """Wrap text in an ANSI color (no-op when colors are disabled)."""
    if not COLOR_ENABLED or not code:
        return text
    return ESC + code + "m" + text + RESET


def clear():
    if _is_tty():
        sys.stdout.write(ESC + "2J" + ESC + "H")
        sys.stdout.flush()


# ==============================================================================
# 2. ANIMATION HELPERS  (lightweight, mobile friendly)
# ==============================================================================

def type_out(text, code=WHITE, delay=0.008, end="\n"):
    """Typewriter effect."""
    if not ANIM:
        sys.stdout.write(paint(text, code) + end)
        sys.stdout.flush()
        return
    for ch in text:
        sys.stdout.write(paint(ch, code))
        sys.stdout.flush()
        if delay:
            time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()


def loading_bar(label, seconds=1.0, width=26, code=GREEN):
    """Smooth progress bar."""
    if not ANIM:
        print(paint("[ OK ] ", GREEN) + paint(label, WHITE))
        return
    steps = width
    delay = seconds / float(steps)
    for i in range(steps + 1):
        filled = "█" * i
        empty = "░" * (width - i)
        pct = int(i * 100 / width)
        sys.stdout.write(
            "\r  " + paint(label.ljust(30), WHITE)
            + " [" + paint(filled, code) + paint(empty, DIM) + "] "
            + paint("%3d%%" % pct, code)
        )
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(
        "\r  " + paint(label.ljust(30), WHITE)
        + " [" + paint("█" * width, GREEN) + "] " + paint("100%", GREEN) + "\n"
    )
    sys.stdout.flush()


def spinner(label, seconds=1.0, code=CYAN):
    """Rotating spinner with a completion tick."""
    frames = ["|", "/", "-", "\\"]
    if not ANIM:
        time.sleep(0.05)
        print(paint("  [OK] ", GREEN) + paint(label, WHITE))
        return
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write("\r  " + paint(frames[i % 4], code) + " " + paint(label, WHITE))
        sys.stdout.flush()
        i += 1
        time.sleep(0.07)
    sys.stdout.write("\r  " + paint("[OK]", GREEN) + " " + paint(label, WHITE) + "\n")
    sys.stdout.flush()


def reveal(text, code=GREEN):
    """Scramble-and-settle reveal effect for the result."""
    if not ANIM:
        for line in text.split("\n"):
            print(paint(line, code))
        return
    noise = "".join(chr(i) for i in range(33, 127))
    for line in text.split("\n"):
        n = len(line)
        if n == 0:
            print()
            continue
        if n > 90:                       # long lines: no \r games
            print(paint(line, code))
            continue
        steps = min(16, n)
        delay = min(0.035, 0.9 / max(steps, 1))
        for s in range(steps + 1):
            shown = int(n * s / steps)
            tail = "".join(random.choice(noise) for _ in range(n - shown))
            sys.stdout.write("\r  " + paint(line[:shown] + tail, code))
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\r  " + paint(line, code) + "\n")
        sys.stdout.flush()


def pause(message="Press ENTER to continue..."):
    try:
        input(paint("\n  " + message, DIM))
    except (EOFError, KeyboardInterrupt):
        raise


# ==============================================================================
# 3. ZERO GHOST MAPPING TABLES  (verbatim from the sheet)
# ==============================================================================
#
# Sheet columns used:
#   ENCRYPT_PAIRS  = (Plain ASCII , Encrypt ASCII)
#   DECRYPT_PAIRS  = (Cipher ASCII, Decrypt ASCII)
#
# ------------------------------------------------------------------------------
# Message Encrypt mapping : Plain ASCII -> Encrypt ASCII
# ------------------------------------------------------------------------------
ENCRYPT_PAIRS = [
    (33, 40), (34, 41), (35, 42), (36, 43), (37, 44), (38, 45), (39, 46), (40, 47), (41, 48), (42, 49),
    (43, 50), (44, 51), (45, 52), (46, 53), (47, 54), (48, 55), (49, 56), (50, 57), (51, 58), (52, 59),
    (53, 60), (54, 61), (55, 62), (56, 63), (57, 64), (58, 65), (59, 66), (60, 67), (61, 68), (62, 69),
    (63, 70), (64, 71), (65, 72), (66, 73), (67, 74), (68, 75), (69, 76), (70, 77), (71, 78), (72, 79),
    (73, 80), (74, 81), (75, 82), (76, 83), (77, 84), (78, 85), (79, 86), (80, 87), (81, 88), (82, 89),
    (83, 90), (84, 91), (85, 92), (86, 93), (87, 94), (88, 95), (89, 96), (90, 97), (91, 98), (92, 99),
    (93, 100), (94, 101), (95, 102), (96, 103), (97, 104), (98, 105), (99, 106), (100, 107), (101, 108), (102, 109),
    (103, 110), (104, 111), (105, 112), (106, 113), (107, 114), (108, 115), (109, 116), (110, 117), (111, 118), (112, 119),
    (113, 120), (114, 121), (115, 122), (116, 123), (117, 124), (118, 125), (119, 126),
    (120, 33), (121, 34), (122, 35), (123, 36), (124, 37), (125, 38), (126, 39),
]

# ------------------------------------------------------------------------------
# Message Decrypt mapping : Cipher ASCII -> Decrypt ASCII
# ------------------------------------------------------------------------------
DECRYPT_PAIRS = [
    (40, 33), (41, 34), (42, 35), (43, 36), (44, 37), (45, 38), (46, 39), (47, 40), (48, 41), (49, 42),
    (50, 43), (51, 44), (52, 45), (53, 46), (54, 47), (55, 48), (56, 49), (57, 50), (58, 51), (59, 52),
    (60, 53), (61, 54), (62, 55), (63, 56), (64, 57), (65, 58), (66, 59), (67, 60), (68, 61), (69, 62),
    (70, 63), (71, 64), (72, 65), (73, 66), (74, 67), (75, 68), (76, 69), (77, 70), (78, 71), (79, 72),
    (80, 73), (81, 74), (82, 75), (83, 76), (84, 77), (85, 78), (86, 79), (87, 80), (88, 81), (89, 82),
    (90, 83), (91, 84), (92, 85), (93, 86), (94, 87), (95, 88), (96, 89), (97, 90), (98, 91), (99, 92),
    (100, 93), (101, 94), (102, 95), (103, 96), (104, 97), (105, 98), (106, 99), (107, 100), (108, 101), (109, 102),
    (110, 103), (111, 104), (112, 105), (113, 106), (114, 107), (115, 108), (116, 109), (117, 110), (118, 111), (119, 112),
    (120, 113), (121, 114), (122, 115), (123, 116), (124, 117), (125, 118), (126, 119),
    (33, 120), (34, 121), (35, 122), (36, 123), (37, 124), (38, 125), (39, 126),
]

ENCRYPT_MAP = {chr(plain): chr(enc) for plain, enc in ENCRYPT_PAIRS}
DECRYPT_MAP = {chr(ciph): chr(dec) for ciph, dec in DECRYPT_PAIRS}


# ==============================================================================
# 4. CORE CIPHER (table driven - no algorithm is invented)
# ==============================================================================

def encrypt_message(text):
    """Map every supported character through the ENCRYPT table."""
    return "".join(ENCRYPT_MAP.get(ch, ch) for ch in text)


def decrypt_message(text):
    """Map every supported character through the DECRYPT table."""
    return "".join(DECRYPT_MAP.get(ch, ch) for ch in text)


# ==============================================================================
# 5. COMPATIBILITY / INTEGRITY SELF-TEST
# ==============================================================================
# Reference implementation of the ORIGINAL Zero Ghost.py MessageCipher.
# It is used ONLY for verification - the program itself never calls it.
REF_SHIFT = 7
REF_MIN = 33
REF_MAX = 126
REF_SPAN = 94


def reference_encrypt(text, shift=REF_SHIFT):
    out = []
    for ch in text:
        o = ord(ch)
        if REF_MIN <= o <= REF_MAX:
            out.append(chr((o - REF_MIN + shift) % REF_SPAN + REF_MIN))
        else:
            out.append(ch)
    return "".join(out)


def reference_decrypt(text, shift=REF_SHIFT):
    out = []
    for ch in text:
        o = ord(ch)
        if REF_MIN <= o <= REF_MAX:
            out.append(chr((o - REF_MIN - shift) % REF_SPAN + REF_MIN))
        else:
            out.append(ch)
    return "".join(out)


def verify_tables(verbose=False):
    """Return a list of problems. Empty list == everything is correct."""
    problems = []

    if len(ENCRYPT_MAP) != 94:
        problems.append("ENCRYPT_MAP has %d entries, expected 94." % len(ENCRYPT_MAP))
    if len(DECRYPT_MAP) != 94:
        problems.append("DECRYPT_MAP has %d entries, expected 94." % len(DECRYPT_MAP))

    # 1. every printable ASCII char is present in both tables
    for code in range(33, 127):
        ch = chr(code)
        if ch not in ENCRYPT_MAP:
            problems.append("ENCRYPT_MAP missing plain char %r (ASCII %d)." % (ch, code))
        if ch not in DECRYPT_MAP:
            problems.append("DECRYPT_MAP missing cipher char %r (ASCII %d)." % (ch, code))

    # 2. the two tables are exact mirror images of one another
    for plain, enc in ENCRYPT_PAIRS:
        if DECRYPT_MAP.get(chr(enc)) != chr(plain):
            problems.append(
                "Table mismatch: ENCRYPT %d->%d but DECRYPT %d->%r."
                % (plain, enc, enc, DECRYPT_MAP.get(chr(enc)))
            )
    for ciph, dec in DECRYPT_PAIRS:
        if ENCRYPT_MAP.get(chr(dec)) != chr(ciph):
            problems.append(
                "Table mismatch: DECRYPT %d->%d but ENCRYPT %d->%r."
                % (ciph, dec, dec, ENCRYPT_MAP.get(chr(dec)))
            )

    # 3. full round-trip over the whole supported range
    for code in range(33, 127):
        ch = chr(code)
        if decrypt_message(encrypt_message(ch)) != ch:
            problems.append("Round-trip failure on ASCII %d." % code)

    # 4. bit-for-bit compatibility with the original Zero Ghost cipher
    for code in range(33, 127):
        ch = chr(code)
        if encrypt_message(ch) != reference_encrypt(ch):
            problems.append("Encrypt differs from original on ASCII %d." % code)
        if decrypt_message(ch) != reference_decrypt(ch):
            problems.append("Decrypt differs from original on ASCII %d." % code)

    # 5. pass-through behaviour (spaces, tabs, newlines, non-ASCII)
    sample = " \t\n\r\u00e9\u4e2d\u00b5"
    if encrypt_message(sample) != sample or decrypt_message(sample) != sample:
        problems.append("Unsupported characters are not being preserved.")

    if verbose:
        for p in problems:
            print(paint("  [!] " + p, RED))
    return problems


# ==============================================================================
# 6. BRANDING / LOGO
# ==============================================================================

LOGO_ZERO = [
    " ███████╗███████╗██████╗  ██████╗ ",
    " ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗",
    "   ███╔╝ █████╗  ██████╔╝██║   ██║",
    "  ███╔╝  ██╔══╝  ██╔══██╗██║   ██║",
    " ███████╗███████╗██║  ██║╚██████╔╝",
    " ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ",
]

LOGO_GHOST = [
    "  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗",
    " ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝",
    " ██║  ███╗███████║██║   ██║███████╗   ██║   ",
    " ██║   ██║██╔══██║██║   ██║╚════██║   ██║   ",
    " ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ",
    "  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ",
]


def show_logo(animate=True):
    """Neon multi-colour ZERO GHOST TEAM logo."""
    colors_a = [GREEN, CYAN, PURPLE, BLUE, CYAN, GREEN]
    colors_b = [PURPLE, RED, YELLOW, GREEN, CYAN, BLUE]
    for i, line in enumerate(LOGO_ZERO):
        print(paint(line, colors_a[i]))
        if animate and ANIM:
            time.sleep(0.04)
    for i, line in enumerate(LOGO_GHOST):
        print(paint(line, colors_b[i]))
        if animate and ANIM:
            time.sleep(0.04)
    print(paint("            T  E  A  M   //   Z E R O   G H O S T", YELLOW))


def banner_small(width=58):
    line = "═" * width
    print(paint("  ╔" + line + "╗", CYAN))
    print(paint("  ║", CYAN) + paint("   ZERO GHOST TEAM  ::  ENCRYPTION SYSTEM  v1.0".ljust(width), GREEN) + paint("║", CYAN))
    print(paint("  ║", CYAN) + paint("   DEVELOPED BY ZERO-X".ljust(width), PURPLE) + paint("║", CYAN))
    print(paint("  ╚" + line + "╝", CYAN))


def box_top(width=58):
    print(paint("  ╔" + "═" * width + "╗", BLUE))


def box_mid(width=58):
    print(paint("  ╠" + "═" * width + "╣", BLUE))


def box_bot(width=58):
    print(paint("  ╚" + "═" * width + "╝", BLUE))


def box_line(text, code=WHITE, width=58):
    print(paint("  ║", BLUE) + paint(text.ljust(width), code) + paint("║", BLUE))


def rule(width=58):
    print(paint("  " + "─" * width, DIM))


# ==============================================================================
# 7. STARTUP SEQUENCE
# ==============================================================================

def startup():
    clear()
    show_logo()
    print()
    type_out("  MADE BY ZERO GHOST TEAM", YELLOW, 0.006)
    type_out("  DEVELOPED BY ZERO-X", CYAN, 0.006)
    type_out("  PROJECT: ZERO GHOST ENCRYPTION SYSTEM", PURPLE, 0.006)
    print()
    type_out("  INITIALIZING ZERO GHOST SYSTEM...", GREEN, 0.006)
    print()
    loading_bar("LOADING ENCRYPTION MAP", 0.9, code=GREEN)
    loading_bar("LOADING DECRYPTION MAP", 0.9, code=CYAN)
    loading_bar("LINKING CIPHER CORE", 0.7, code=PURPLE)
    loading_bar("RUNNING MAPPING INTEGRITY CHECK", 0.9, code=YELLOW)
    print()

    problems = verify_tables()
    if problems:
        print(paint("  [!] MAPPING INTEGRITY FAILURE:", RED))
        for p in problems[:8]:
            print(paint("      - " + p, RED))
        print(paint("  [!] Continuing is not recommended.", RED))
    else:
        type_out("  [OK] ENCRYPTION MAP VERIFIED  (94 / 94 entries)", GREEN, 0.004)
        type_out("  [OK] DECRYPTION MAP VERIFIED  (94 / 94 entries)", GREEN, 0.004)
        type_out("  [OK] COMPATIBLE WITH ORIGINAL ZERO GHOST CIPHER", GREEN, 0.004)

    print()
    type_out("  SYSTEM READY.", GREEN, 0.02)
    time.sleep(0.5)


# ==============================================================================
# 8. MULTI-LINE INPUT  (3 empty ENTERs = finish)
# ==============================================================================

def read_multiline(title):
    """
    Read a multi-line message.

      * Every non-empty line is added to the message.
      * Up to 2 consecutive empty lines are preserved inside the message.
      * 3 consecutive empty ENTER presses END the input.
    """
    print(paint(title, YELLOW))
    print(paint("  Multi-line mode: press ENTER after each line.", CYAN))
    print(paint("  Press ENTER on 3 empty lines in a row to finish.", CYAN))
    print()

    lines = []
    blank_run = 0
    line_no = 1

    while True:
        prompt = "  %3d | " % line_no
        try:
            line = input(paint(prompt, GREEN))
        except (EOFError, KeyboardInterrupt):
            raise

        if line == "":
            blank_run += 1
            if blank_run >= 3:
                print(paint("  [OK] End of message.", GREEN))
                break
            lines.append("")
            line_no += 1
            if blank_run == 1:
                print(paint("       (press ENTER 2 more times to finish)", DIM))
            else:
                print(paint("       (press ENTER 1 more time to finish)", DIM))
        else:
            blank_run = 0
            lines.append(line)
            line_no += 1

    # Drop trailing empty lines (e.g. 1 or 2 blanks typed right before quitting)
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


# ==============================================================================
# 9. CLIPBOARD  (Termux / iSH / Linux / macOS / Windows)
# ==============================================================================

def _try_termux_clipboard(text):
    """Termux: use termux-clipboard-set if it is installed."""
    is_termux = bool(
        os.environ.get("TERMUX_VERSION")
        or "com.termux" in os.environ.get("PREFIX", "")
    )
    if not is_termux:
        return False
    if not shutil.which("termux-clipboard-set"):
        return False
    try:
        proc = subprocess.run(
            ["termux-clipboard-set"],
            input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _try_pbcopy(text):
    """macOS / iSH (if pbcopy is exposed by the emulator)."""
    if not shutil.which("pbcopy"):
        return False
    try:
        proc = subprocess.run(
            ["pbcopy"],
            input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _try_linux_clipboard(text):
    """wl-copy / xclip / xsel on Linux desktops."""
    payload = text.encode("utf-8")
    candidates = [
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    ]
    for cmd in candidates:
        if not shutil.which(cmd[0]):
            continue
        try:
            proc = subprocess.run(
                cmd,
                input=payload,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            if proc.returncode == 0:
                return True
        except Exception:
            continue
    return False


def _try_windows_clip(text):
    """Windows: pipe UTF-16-LE text through clip.exe."""
    if os.name != "nt":
        return False
    try:
        proc = subprocess.run(
            ["clip"],
            input=text.encode("utf-16-le"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _try_tkinter(text):
    """Desktop Tk clipboard (Windows / macOS / X11 desktops)."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update_idletasks()
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def _try_osc52(text):
    """
    Universal terminal fallback.

    Supported by Termux, iSH, iTerm2, kitty, WezTerm, foot, alacritty
    (with OSC-52 enabled), and most modern terminal emulators.
    """
    try:
        payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
        sys.stdout.write("\033]52;c;" + payload + "\a")
        sys.stdout.flush()
        return True
    except Exception:
        return False


def copy_to_clipboard(text):
    """Try every available clipboard backend. Returns the method name or None."""
    if _try_termux_clipboard(text):
        return "termux-clipboard-set"
    if _try_pbcopy(text):
        return "pbcopy"
    if _try_linux_clipboard(text):
        return "wl-copy/xclip/xsel"
    if _try_windows_clip(text):
        return "clip.exe"
    if _try_tkinter(text):
        return "tkinter"
    if _try_osc52(text):
        return "OSC-52"
    return None


# ==============================================================================
# 10. FILE HELPERS
# ==============================================================================

def save_to_file(text):
    default = "zero_ghost_output.txt"
    try:
        name = input(paint("  FILENAME [%s] > " % default, YELLOW)).strip()
    except (EOFError, KeyboardInterrupt):
        raise
    if not name:
        name = default
    try:
        with open(name, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    except OSError as exc:
        print(paint("  [!] Could not save file: %s" % exc, RED))
        return
    print(paint("  [+] Saved to: %s" % os.path.abspath(name), GREEN))


# ==============================================================================
# 11. RESULT ACTIONS
# ==============================================================================

def result_actions(text, kind):
    """kind == 'encrypted' or 'decrypted'"""
    while True:
        print()
        rule()
        print(paint("  [1] SAVE TO FILE    [2] COPY RESULT    [0] BACK TO MENU", CYAN))
        try:
            choice = input(paint("  SELECT > ", YELLOW)).strip()
        except (EOFError, KeyboardInterrupt):
            raise
        if choice == "1":
            save_to_file(text)
        elif choice == "2":
            method = copy_to_clipboard(text)
            if method:
                print(paint("  [+] %s message copied (via %s)."
                            % (kind.capitalize(), method), GREEN))
            else:
                print(paint("  [!] No clipboard method available. Use SAVE TO FILE.", RED))
        elif choice in ("0", ""):
            return
        else:
            print(paint("  [!] Invalid option. Choose 1, 2 or 0.", RED))


# ==============================================================================
# 12. ENCRYPT / DECRYPT SCREENS
# ==============================================================================

def encrypt_flow():
    clear()
    banner_small()
    print()
    print(paint("  [ ENCRYPTION MODE ]", GREEN))
    rule()
    print(paint("  Supported  : printable ASCII 33-126 (94 characters)", CYAN))
    print(paint("  Unchanged  : spaces, tabs, newlines, non-ASCII", CYAN))
    print()
    try:
        message = read_multiline("  ENTER MESSAGE (multi-line)")
    except (EOFError, KeyboardInterrupt):
        raise

    if message == "":
        print(paint("\n  [!] Empty message - nothing to encrypt.", RED))
        pause()
        return

    print()
    spinner("ENCRYPTING MESSAGE", 1.0, GREEN)
    result = encrypt_message(message)
    print()
    print(paint("  ENCRYPTED MESSAGE:", GREEN))
    rule()
    reveal(result, GREEN)
    rule()
    result_actions(result, "encrypted")


def decrypt_flow():
    clear()
    banner_small()
    print()
    print(paint("  [ DECRYPTION MODE ]", CYAN))
    rule()
    print(paint("  Supported  : printable ASCII 33-126 (94 characters)", CYAN))
    print(paint("  Unchanged  : spaces, tabs, newlines, non-ASCII", CYAN))
    print()
    try:
        message = read_multiline("  ENTER ENCRYPTED MESSAGE (multi-line)")
    except (EOFError, KeyboardInterrupt):
        raise

    if message == "":
        print(paint("\n  [!] Empty message - nothing to decrypt.", RED))
        pause()
        return

    print()
    spinner("DECRYPTING MESSAGE", 1.0, CYAN)
    result = decrypt_message(message)
    print()
    print(paint("  DECRYPTED MESSAGE:", CYAN))
    rule()
    reveal(result, CYAN)
    rule()
    result_actions(result, "decrypted")


# ==============================================================================
# 13. MAIN MENU
# ==============================================================================

def main_menu():
    while True:
        clear()
        banner_small()
        print()
        box_top()
        box_line("                      MAIN MENU", WHITE)
        box_mid()
        box_line("   [1]  ENCRYPT MESSAGE", GREEN)
        box_line("   [2]  DECRYPT MESSAGE", CYAN)
        box_mid()
        box_line("   [0]  EXIT SYSTEM", RED)
        box_bot()
        print()
        print(paint("  ZERO GHOST TEAM  //  POWERED BY ZERO-X", PURPLE))
        print()

        try:
            choice = input(paint("  SELECT OPTION > ", YELLOW)).strip()
        except (EOFError, KeyboardInterrupt):
            raise

        if choice == "1":
            encrypt_flow()
        elif choice == "2":
            decrypt_flow()
        elif choice in ("0", "q", "Q", "exit", "EXIT"):
            shutdown()
        else:
            print(paint("  [!] Invalid option. Please choose 1, 2 or 0.", RED))
            time.sleep(0.7)


def shutdown():
    clear()
    banner_small()
    print()
    type_out("  CLOSING SECURE CHANNEL...", PURPLE, 0.01)
    loading_bar("WIPING SESSION MEMORY", 0.7, code=RED)
    print()
    type_out("  ZERO GHOST TEAM // ZERO-X  -  STAY INVISIBLE.", GREEN, 0.01)
    print()
    sys.exit(0)


# ==============================================================================
# 14. SELF-TEST MODE  (python3 zero_ghost.py --selftest)
# ==============================================================================

def run_selftest():
    print("=" * 70)
    print(" ZERO GHOST - MAPPING & COMPATIBILITY SELF-TEST")
    print("=" * 70)
    print(" ENCRYPT_MAP entries : %d" % len(ENCRYPT_MAP))
    print(" DECRYPT_MAP entries : %d" % len(DECRYPT_MAP))
    problems = verify_tables()
    print(" Table / round-trip / reference-cipher problems: %d" % len(problems))
    for p in problems:
        print("   [!] " + p)
    print("-" * 70)
    samples = [
        "HELLO WORLD",
        "Zero Ghost",
        "P@ssw0rd!",
        "The quick brown fox jumps over the lazy dog 0123456789",
        "Symbols: !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
        "Spaces   and\ttabs\nand newlines stay intact.",
        "Line 1\n\nLine 3 after a blank line\n\n\nStill inside the message",
        "Unicode: café 中文 ünïcode",
    ]
    ok = True
    for s in samples:
        e = encrypt_message(s)
        d = decrypt_message(e)
        ref_e = reference_encrypt(s)
        ref_d = reference_decrypt(e)
        status = "PASS"
        if d != s or e != ref_e or ref_d != s:
            status = "FAIL"
            ok = False
        print(" [%s] %r" % (status, s))
        print("        enc : %r" % e)
        print("        dec : %r" % d)
    print("-" * 70)
    print(" Clipboard backend available: %s" % (copy_to_clipboard("zero ghost ping") or "NONE"))
    print("-" * 70)
    print(" RESULT: %s" % ("ALL CHECKS PASSED" if ok and not problems else "FAILURES DETECTED"))
    print("=" * 70)
    return 0 if (ok and not problems) else 1


# ==============================================================================
# 15. ENTRY POINT
# ==============================================================================

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--selftest", "-t", "--test"):
        sys.exit(run_selftest())
    try:
        startup()
        main_menu()
    except KeyboardInterrupt:
        print()
        print(paint("\n  [!] SESSION TERMINATED BY USER. GOODBYE.", RED))
        print()
        sys.exit(0)
    except EOFError:
        print()
        print(paint("\n  [!] INPUT STREAM CLOSED. GOODBYE.", RED))
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()