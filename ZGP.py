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
     SHIFT = 7  |  Printable ASCII 33-126 (94 chars)
     Encrypt : +7 in the 94-char ring
     Decrypt : -7 in the 94-char ring
     Unchanged : spaces, tabs, newlines, non-ASCII
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
# 1. TERMINAL / COLOR LAYER
# ==============================================================================

ESC = "\033["
RESET = ESC + "0m"


def _enable_windows_vt():
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

GREEN  = "1;92"
CYAN   = "1;96"
PURPLE = "1;95"
RED    = "1;91"
BLUE   = "1;94"
YELLOW = "1;93"
WHITE  = "1;97"
DIM    = "2"

PALETTE = [GREEN, CYAN, PURPLE, RED, BLUE, YELLOW]


def paint(text, code=""):
    if not COLOR_ENABLED or not code:
        return text
    return ESC + code + "m" + text + RESET


def clear():
    if _is_tty():
        sys.stdout.write(ESC + "2J" + ESC + "H")
        sys.stdout.flush()


def clear_line():
    if _is_tty():
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()


# ==============================================================================
# 2. ANIMATION HELPERS
# ==============================================================================

def type_out(text, code=WHITE, delay=0.008, end="\n"):
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


def loading_bar(label, seconds=0.55, width=10, code=GREEN):
    if not ANIM:
        return
    steps = width
    delay = seconds / float(steps)
    for i in range(steps + 1):
        filled = "█" * i
        empty = "░" * (width - i)
        pct = int(i * 100 / width)
        sys.stdout.write(
            "\r  " + paint(label.ljust(15), WHITE)
            + " [" + paint(filled, code) + paint(empty, DIM) + "] "
            + paint("%3d%%" % pct, code)
        )
        sys.stdout.flush()
        time.sleep(delay)
    clear_line()


def spinner(label, seconds=0.8, code=CYAN):
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
        if n > 40:
            print(paint(line, code))
            continue
        steps = min(14, n)
        delay = min(0.035, 0.7 / max(steps, 1))
        for s in range(steps + 1):
            shown = int(n * s / steps)
            tail = "".join(random.choice(noise) for _ in range(n - shown))
            sys.stdout.write("\r  " + paint(line[:shown] + tail, code))
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\r  " + paint(line, code) + "\n")
        sys.stdout.flush()


def pause(message="ENTER to continue..."):
    try:
        input(paint("\n  " + message, DIM))
    except (EOFError, KeyboardInterrupt):
        raise


# ==============================================================================
# 3. ZERO GHOST MAPPING TABLES  (verbatim from the sheet)
# ==============================================================================

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
# 4. CORE CIPHER
# ==============================================================================

def encrypt_message(text):
    return "".join(ENCRYPT_MAP.get(ch, ch) for ch in text)


def decrypt_message(text):
    return "".join(DECRYPT_MAP.get(ch, ch) for ch in text)


# ==============================================================================
# 5. SELF-TEST / COMPATIBILITY
# ==============================================================================

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
    problems = []

    if len(ENCRYPT_MAP) != 94:
        problems.append("ENCRYPT_MAP has %d entries, expected 94." % len(ENCRYPT_MAP))
    if len(DECRYPT_MAP) != 94:
        problems.append("DECRYPT_MAP has %d entries, expected 94." % len(DECRYPT_MAP))

    for code in range(33, 127):
        ch = chr(code)
        if ch not in ENCRYPT_MAP:
            problems.append("ENCRYPT_MAP missing %r." % ch)
        if ch not in DECRYPT_MAP:
            problems.append("DECRYPT_MAP missing %r." % ch)

    for plain, enc in ENCRYPT_PAIRS:
        if DECRYPT_MAP.get(chr(enc)) != chr(plain):
            problems.append("Table mismatch: ENCRYPT %d->%d." % (plain, enc))
    for ciph, dec in DECRYPT_PAIRS:
        if ENCRYPT_MAP.get(chr(dec)) != chr(ciph):
            problems.append("Table mismatch: DECRYPT %d->%d." % (ciph, dec))

    for code in range(33, 127):
        ch = chr(code)
        if decrypt_message(encrypt_message(ch)) != ch:
            problems.append("Round-trip failure on ASCII %d." % code)
        if encrypt_message(ch) != reference_encrypt(ch):
            problems.append("Encrypt differs on ASCII %d." % code)
        if decrypt_message(ch) != reference_decrypt(ch):
            problems.append("Decrypt differs on ASCII %d." % code)

    sample = " \t\n\r\u00e9\u4e2d\u00b5"
    if encrypt_message(sample) != sample or decrypt_message(sample) != sample:
        problems.append("Unsupported chars not preserved.")

    if verbose:
        for p in problems:
            print(paint("  [!] " + p, RED))
    return problems


# ==============================================================================
# 6. UI: BANNER + SEPARATORS
# ==============================================================================

SEP = "=" * 48


def sep(color=CYAN):
    print(paint(SEP, color))


def show_banner():
    art = [
        (" ███████╗███████╗██████╗  ██████╗ ", GREEN),
        (" ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗", CYAN),
        ("   ███╔╝ █████╗  ██████╔╝██║   ██║", PURPLE),
        ("  ███╔╝  ██╔══╝  ██╔══██╗██║   ██║", BLUE),
        (" ███████╗███████╗██║  ██║╚██████╔╝", YELLOW),
        (" ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ", RED),
    ]
    print()
    for text, color in art:
        print(paint("     " + text, color))
    print(paint("         Z E R O   G H O S T   T E A M", YELLOW))
    print()


# ==============================================================================
# 7. STARTUP SEQUENCE
# ==============================================================================

def startup():
    clear()
    show_banner()
    type_out("        MADE BY ZERO GHOST TEAM", YELLOW, 0.006)
    type_out("        DEVELOPED BY ZERO-X", CYAN, 0.006)
    print()
    type_out("  INITIALIZING ZERO GHOST SYSTEM...", GREEN, 0.006)
    print()

    loading_bar("ENCRYPTION MAP",  0.55, code=GREEN)
    loading_bar("DECRYPTION MAP",  0.55, code=CYAN)
    loading_bar("CIPHER CORE",     0.45, code=PURPLE)
    loading_bar("INTEGRITY CHECK", 0.55, code=YELLOW)

    problems = verify_tables()
    if problems:
        print(paint("  [!] MAPPING FAILURE:", RED))
        for p in problems[:4]:
            print(paint("      - " + p, RED))
        print(paint("  [!] Continuing not recommended.", RED))
    else:
        print(paint("  [OK] ENCRYPTION MAP  (94/94)", GREEN))
        print(paint("  [OK] DECRYPTION MAP  (94/94)", GREEN))
        print(paint("  [OK] COMPATIBLE WITH ORIGINAL", GREEN))

    print()
    type_out("  SYSTEM READY.", GREEN, 0.02)
    time.sleep(0.4)


# ==============================================================================
# 8. MULTI-LINE INPUT + EDITOR
# ==============================================================================

def _collect_lines(start_line, initial_lines):
    """Collect lines with 3 empty ENTERs to finish. No '>' prompt."""
    lines = list(initial_lines)
    line_no = start_line
    blank_run = 0
    while True:
        try:
            line = input(paint("  %2d  " % line_no, GREEN))
        except (EOFError, KeyboardInterrupt):
            raise
        if line == "":
            blank_run += 1
            if blank_run >= 3:
                return lines
            lines.append("")
        else:
            blank_run = 0
            lines.append(line)
        line_no += 1


def _show_lines(lines):
    print()
    print(paint("  --- YOUR LINES ---", CYAN))
    if not lines:
        print(paint("  (empty)", DIM))
    else:
        for i, l in enumerate(lines, 1):
            print(paint("  %2d  %s" % (i, l), WHITE))
    print()


def _edit_menu(lines):
    """
    Interactive line editor.

    Editing line N replaces ONLY line N. All other lines stay intact.
    Returns the final list of lines, or None if the user quit.
    """
    lines = list(lines)
    while True:
        _show_lines(lines)
        print(paint("  :N=edit N   :D N=delete N   :A=append   :0=done   :Q=quit", DIM))
        try:
            cmd = input(paint("  > ", YELLOW)).strip()
        except (EOFError, KeyboardInterrupt):
            raise

        if cmd in ("", "0", ":0"):
            while lines and lines[-1] == "":
                lines.pop()
            return lines

        if cmd in (":Q", ":q"):
            return None

        if cmd in (":A", ":a"):
            lines = _collect_lines(len(lines) + 1, lines)
            continue

        if cmd.startswith(":D ") or cmd.startswith(":d "):
            try:
                n = int(cmd[3:].strip())
                if 1 <= n <= len(lines):
                    del lines[n - 1]
                else:
                    print(paint("  [!] Line %d not found." % n, RED))
            except ValueError:
                print(paint("  [!] Invalid line number.", RED))
            continue

        num_str = cmd[1:] if cmd.startswith(":") else cmd
        if num_str.isdigit():
            n = int(num_str)
            if 1 <= n <= len(lines):
                try:
                    new = input(paint("  new %d: " % n, CYAN))
                except (EOFError, KeyboardInterrupt):
                    raise
                lines[n - 1] = new
                print(paint("  [+] Line %d updated (others unchanged)." % n, GREEN))
                time.sleep(0.35)
            else:
                print(paint("  [!] Line %d not found." % n, RED))
        else:
            print(paint("  [!] Unknown command: %s" % cmd, RED))


# ==============================================================================
# 9. CLIPBOARD  READ + WRITE
# ==============================================================================

def _read_termux_clipboard():
    is_termux = bool(
        os.environ.get("TERMUX_VERSION")
        or "com.termux" in os.environ.get("PREFIX", "")
    )
    if not is_termux:
        return None
    if not shutil.which("termux-clipboard-get"):
        return None
    try:
        r = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="replace")
    except Exception:
        pass
    return None


def _read_pbpaste():
    if not shutil.which("pbpaste"):
        return None
    try:
        r = subprocess.run(["pbpaste"], capture_output=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="replace")
    except Exception:
        pass
    return None


def _read_linux_clipboard():
    for cmd in (
        ["wl-paste", "--no-newline"],
        ["xclip", "-selection", "clipboard", "-o"],
        ["xsel", "--clipboard", "--output"],
    ):
        if not shutil.which(cmd[0]):
            continue
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=5)
            if r.returncode == 0:
                return r.stdout.decode("utf-8", errors="replace")
        except Exception:
            continue
    return None


def _read_windows_clip():
    if os.name != "nt":
        return None
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
            capture_output=True, timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="replace").rstrip("\r\n")
    except Exception:
        pass
    return None


def _read_tkinter():
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        try:
            t = root.clipboard_get()
        except Exception:
            t = None
        root.destroy()
        return t
    except Exception:
        return None


def read_clipboard():
    t = _read_termux_clipboard()
    if t is not None:
        return t
    t = _read_pbpaste()
    if t is not None:
        return t
    t = _read_linux_clipboard()
    if t is not None:
        return t
    t = _read_windows_clip()
    if t is not None:
        return t
    t = _read_tkinter()
    if t is not None:
        return t
    return None


def _try_termux_clipboard(text):
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
    if not shutil.which("pbcopy"):
        return False
    try:
        proc = subprocess.run(
            ["pbcopy"], input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _try_linux_clipboard(text):
    payload = text.encode("utf-8")
    for cmd in (
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    ):
        if not shutil.which(cmd[0]):
            continue
        try:
            proc = subprocess.run(
                cmd, input=payload,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
            )
            if proc.returncode == 0:
                return True
        except Exception:
            continue
    return False


def _try_windows_clip(text):
    if os.name != "nt":
        return False
    try:
        proc = subprocess.run(
            ["clip"], input=text.encode("utf-16-le"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _try_tkinter_set(text):
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
    try:
        payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
        sys.stdout.write("\033]52;c;" + payload + "\a")
        sys.stdout.flush()
        return True
    except Exception:
        return False


def copy_to_clipboard(text):
    if _try_termux_clipboard(text):
        return "termux-clipboard-set"
    if _try_pbcopy(text):
        return "pbcopy"
    if _try_linux_clipboard(text):
        return "wl-copy/xclip/xsel"
    if _try_windows_clip(text):
        return "clip.exe"
    if _try_tkinter_set(text):
        return "tkinter"
    if _try_osc52(text):
        return "OSC-52"
    return None


# ==============================================================================
# 10. PASTE PROMPT + CONFIRM
# ==============================================================================

def ask_paste():
    print()
    sep(CYAN)
    print(paint("     PASTE YOUR COPIED CLIPBOARD?", YELLOW))
    print()
    print(paint("     [1] YES", GREEN))
    print(paint("     [2] NO", RED))
    sep(CYAN)
    print()
    while True:
        try:
            choice = input(paint("  > ", YELLOW)).strip()
        except (EOFError, KeyboardInterrupt):
            raise
        if choice == "1":
            return True
        if choice in ("2", ""):
            return False
        print(paint("  [!] Choose 1 or 2.", RED))


def show_pasted_and_confirm(text):
    """Show the pasted text and ask [1] Confirm / [2] Edit."""
    print()
    sep(CYAN)
    print(paint("     PASTED FROM CLIPBOARD", CYAN))
    sep(CYAN)
    print()
    lines = text.split("\n")
    for l in lines:
        print(paint("  " + l, WHITE))
    print()
    print(paint("  (%d lines, %d chars)" % (len(lines), len(text)), DIM))
    print()
    sep(CYAN)
    print(paint("     [1] Confirm and process", GREEN))
    print(paint("     [2] Edit the text", YELLOW))
    sep(CYAN)
    print()
    while True:
        try:
            choice = input(paint("  > ", YELLOW)).strip()
        except (EOFError, KeyboardInterrupt):
            raise
        if choice == "1":
            return "confirm"
        if choice == "2":
            return "edit"
        print(paint("  [!] Choose 1 or 2.", RED))


# ==============================================================================
# 11. MODE HEADER / INPUT SECTION RENDERERS
# ==============================================================================

def render_mode_header(mode_label):
    clear()
    sep(CYAN)
    show_banner()
    sep(CYAN)
    print()
    color = GREEN if mode_label == "Encrypt" else CYAN
    print(paint("     %s THE MESSAGE HERE" % mode_label.upper(), color))
    sep(color)
    print()


def render_input_section(mode_label):
    print(paint("Note : Skip 3 Lines for Enter", YELLOW))
    sep(CYAN)
    print()
    print(paint("     Write/Paste Your Message to %s" % mode_label, CYAN))
    sep(CYAN)
    print()


# ==============================================================================
# 12. MESSAGE ACQUISITION FLOW
# ==============================================================================

def get_message(mode_label):
    """
    Full acquisition flow.

    Returns:
      * str  -> the final message text
      * ""   -> empty (nothing entered)
      * None -> user cancelled (:Q)
    """
    if ask_paste():
        content = read_clipboard()
        if content:
            content = content.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
            action = show_pasted_and_confirm(content)
            if action == "confirm":
                return content
            # Edit mode: clear UI, show pasted lines in editor
            render_mode_header(mode_label)
            print(paint("     EDIT YOUR MESSAGE", CYAN))
            sep(CYAN)
            lines = _edit_menu(content.split("\n"))
            if lines is None:
                return None
            return "\n".join(lines)
        else:
            print(paint("  [!] Clipboard empty or unavailable.", RED))
            print(paint("      Falling back to manual input.", DIM))
            time.sleep(1.0)

    # Manual input
    render_input_section(mode_label)
    lines = _collect_lines(1, [])
    lines = _edit_menu(lines)
    if lines is None:
        return None
    return "\n".join(lines)


# ==============================================================================
# 13. RESULT — single option: ENTER to copy, then back to menu
# ==============================================================================

def result_and_return(text):
    print()
    sep(GREEN)
    print(paint("     Press ENTER to COPY and return to MENU", YELLOW))
    sep(GREEN)
    print()
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass

    method = copy_to_clipboard(text)
    print()
    if method:
        print(paint("  [+] Copied to clipboard (%s)." % method, GREEN))
    else:
        print(paint("  [!] Clipboard unavailable on this terminal.", RED))
    time.sleep(1.2)


# ==============================================================================
# 14. ENCRYPT / DECRYPT FLOWS
# ==============================================================================

def encrypt_flow():
    render_mode_header("Encrypt")

    message = get_message("Encrypt")
    if message is None:
        return
    if message == "":
        print()
        print(paint("  [!] Empty message.", RED))
        pause()
        return

    print()
    sep(CYAN)
    print()
    spinner("ENCRYPTING", 0.9, GREEN)
    result = encrypt_message(message)

    print()
    sep(GREEN)
    print(paint("     ENCRYPTED MESSAGE", GREEN))
    sep(GREEN)
    print()
    reveal(result, GREEN)

    result_and_return(result)


def decrypt_flow():
    render_mode_header("Decrypt")

    message = get_message("Decrypt")
    if message is None:
        return
    if message == "":
        print()
        print(paint("  [!] Empty message.", RED))
        pause()
        return

    print()
    sep(CYAN)
    print()
    spinner("DECRYPTING", 0.9, CYAN)
    result = decrypt_message(message)

    print()
    sep(CYAN)
    print(paint("     DECRYPTED MESSAGE", CYAN))
    sep(CYAN)
    print()
    reveal(result, CYAN)

    result_and_return(result)


# ==============================================================================
# 15. MAIN MENU
# ==============================================================================

def main_menu():
    while True:
        clear()
        sep(CYAN)
        show_banner()
        sep(CYAN)
        print()
        print(paint("1 > ENCRYPT THE MESSAGE", GREEN))
        print(paint("2 > DECRYPT THE MESSAGE", CYAN))
        print()
        print(paint("0 > EXIT THE SYSTEM", RED))
        print()
        sep(CYAN)
        print(paint("     Developed By Zero - X", PURPLE))
        sep(CYAN)
        print()

        try:
            choice = input(paint("  > ", YELLOW)).strip()
        except (EOFError, KeyboardInterrupt):
            raise

        if choice == "1":
            encrypt_flow()
        elif choice == "2":
            decrypt_flow()
        elif choice in ("0", "q", "Q", "exit", "EXIT"):
            shutdown()
        else:
            print(paint("  [!] Choose 1, 2 or 0.", RED))
            time.sleep(0.6)


def shutdown():
    clear()
    sep(CYAN)
    show_banner()
    sep(CYAN)
    print()
    type_out("  CLOSING SECURE CHANNEL...", PURPLE, 0.01)
    loading_bar("WIPING SESSION", 0.45, code=RED)
    print()
    type_out("  ZERO GHOST TEAM // ZERO-X", GREEN, 0.01)
    type_out("  STAY INVISIBLE.", GREEN, 0.01)
    print()
    sys.exit(0)


# ==============================================================================
# 16. SELF-TEST MODE
# ==============================================================================

def run_selftest():
    print("=" * 48)
    print(" ZERO GHOST - SELF-TEST")
    print("=" * 48)
    print(" ENCRYPT_MAP entries : %d" % len(ENCRYPT_MAP))
    print(" DECRYPT_MAP entries : %d" % len(DECRYPT_MAP))
    problems = verify_tables()
    print(" Problems: %d" % len(problems))
    for p in problems:
        print("   [!] " + p)
    print("-" * 48)
    samples = [
        "HELLO WORLD",
        "Zero Ghost",
        "P@ssw0rd!",
        "The quick brown fox 0123456789",
        "Symbols: !\"#$%&'()*+,-./",
        "Line 1\n\nLine 3 after blank",
        "Unicode: caf\u00e9 \u4e2d\u6587",
    ]
    ok = True
    for s in samples:
        e = encrypt_message(s)
        d = decrypt_message(e)
        status = "PASS"
        if d != s or e != reference_encrypt(s):
            status = "FAIL"
            ok = False
        print(" [%s] %r" % (status, s))
        print("   enc: %r" % e)
        print("   dec: %r" % d)
    print("-" * 48)
    print(" Clipboard read : %s" % ("OK" if read_clipboard() is not None else "NONE"))
    print(" Clipboard write: %s" % (copy_to_clipboard("zero ghost ping") or "NONE"))
    print("-" * 48)
    print(" RESULT: %s" % ("ALL PASSED" if ok and not problems else "FAILURES"))
    print("=" * 48)
    return 0 if (ok and not problems) else 1


# ==============================================================================
# 17. ENTRY POINT
# ==============================================================================

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--selftest", "-t", "--test"):
        sys.exit(run_selftest())
    try:
        startup()
        main_menu()
    except KeyboardInterrupt:
        print()
        print(paint("\n  [!] TERMINATED BY USER.", RED))
        print()
        sys.exit(0)
    except EOFError:
        print()
        print(paint("\n  [!] INPUT CLOSED.", RED))
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
