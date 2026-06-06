"""
src/tui/scrambler_menu.py
=========================
Interactive TUI for the multi-layer password scrambler.

Kept separate from scrambler.py (pure crypto logic) so a future GUI layer
can import and call the same underlying functions without touching this file.
"""

import questionary
from questionary import Style

from src.scrambler import (
    DEFAULT_KEY_FILE,
    fernet_keygen,
    vigenere_encrypt,
    vigenere_decrypt,
    fernet_encrypt,
    fernet_decrypt,
    stacked_encrypt,
    stacked_decrypt,
    process_file,
)
from src.utils.utils import ask_for_path_and_validate, ask_for_key_and_validate


# ── Shared style ──────────────────────────────────────────────────────────────

STYLE = Style([
    ("qmark",     "fg:#00aabb bold"),
    ("question",  "bold"),
    ("answer",    "fg:#00aabb bold"),
    ("pointer",   "fg:#00aabb bold"),
    ("selected",  "fg:#00aabb"),
])

_MODES = [
    questionary.Choice("Vigenère only",   value="vigenere"),
    questionary.Choice("Fernet only",     value="fernet"),
    questionary.Choice("Stacked (both)",  value="stacked"),
]


# ── Key-input helpers ─────────────────────────────────────────────────────────

def _get_vigenere_key(confirm: bool = False) -> str:
    """Prompt for a Vigenère key, with optional confirmation."""
    if confirm:
        while True:
            key = questionary.password(
                "Enter Vigenère key:", style=STYLE
            ).ask()
            again = questionary.password(
                "Confirm Vigenère key:", style=STYLE
            ).ask()
            if key == again:
                return key
            questionary.print("Keys do not match — try again.", style="fg:#ff6b6b")
    return questionary.password("Enter Vigenère key:", style=STYLE).ask()


def _get_fernet_source(encrypting: bool) -> tuple[str | None, str | None]:
    """
    Ask whether the user wants to type a key/passphrase or load from a file.
    Delegates to the shared ask_for_key_and_validate helper for the inline path
    (which handles confirmation on encrypt) and ask_for_path_and_validate for
    the file path.

    Returns (fkey, key_file) — one populated, the other None.
    """
    source = questionary.select(
        "Fernet key source:",
        choices=[
            questionary.Choice("Type a key or passphrase", value="inline"),
            questionary.Choice("Load from file",            value="file"),
        ],
        pointer="->",
        style=STYLE,
    ).ask()

    if source == "inline":
        return ask_for_key_and_validate(locking=encrypting)

    key_file = ask_for_path_and_validate("Path to Fernet key file")
    return (None, key_file)


def _collect_keys(mode: str, encrypting: bool) -> tuple[str | None, str | None, str | None]:
    """
    Gather whichever keys the chosen mode requires.

    Returns (vkey, fkey, key_file).
    """
    vkey = fkey = key_file = None

    if mode in ("vigenere", "stacked"):
        vkey = _get_vigenere_key(confirm=encrypting)

    if mode in ("fernet", "stacked"):
        fkey, key_file = _get_fernet_source(encrypting=encrypting)

    return vkey, fkey, key_file


# ── Action handlers ───────────────────────────────────────────────────────────

def _handle_keygen() -> None:
    out = questionary.text(
        "Save key to:",
        default=DEFAULT_KEY_FILE,
        style=STYLE,
    ).ask().strip() or DEFAULT_KEY_FILE

    try:
        key = fernet_keygen(out)
        questionary.print(f"✓ Key saved to '{out}':\n  {key}", style="fg:#00bb77 bold")
    except RuntimeError as exc:
        questionary.print(f"✗ {exc}", style="fg:#ff6b6b bold")


def _handle_single(encrypting: bool) -> None:
    verb = "Encrypt" if encrypting else "Decrypt"

    mode = questionary.select(
        "Mode:",
        choices=_MODES,
        pointer="->",
        style=STYLE,
    ).ask()

    prompt = "Plaintext:" if encrypting else "Ciphertext:"
    text = questionary.text(prompt, style=STYLE).ask()

    vkey, fkey, key_file = _collect_keys(mode, encrypting)

    try:
        if encrypting:
            if mode == "vigenere":
                result = vigenere_encrypt(text, vkey)
            elif mode == "fernet":
                result = fernet_encrypt(text, fkey=fkey, key_file=key_file)
            else:
                result = stacked_encrypt(text, vkey, fkey=fkey, key_file=key_file)
        else:
            if mode == "vigenere":
                result = vigenere_decrypt(text, vkey)
            elif mode == "fernet":
                result = fernet_decrypt(text, fkey=fkey, key_file=key_file)
            else:
                result = stacked_decrypt(text, vkey, fkey=fkey, key_file=key_file)

        label = "Encrypted" if encrypting else "Decrypted"
        questionary.print(f"\n{label}: {result}", style="fg:#00bb77 bold")

    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        questionary.print(f"✗ {exc}", style="fg:#ff6b6b bold")


def _handle_file(encrypting: bool) -> None:
    mode = questionary.select(
        "Mode:",
        choices=_MODES,
        pointer="->",
        style=STYLE,
    ).ask()

    in_path  = ask_for_path_and_validate("Input file (one password per line)")
    out_path = questionary.text(
        "Output file:",
        default=in_path.removesuffix(".txt") + ("_encrypted.txt" if encrypting else "_decrypted.txt"),
        style=STYLE,
        validate=lambda t: len(t.strip()) > 0 or "Path cannot be empty",
    ).ask().strip()

    if ".txt" not in out_path:
        out_path += ".txt"

    vkey, fkey, key_file = _collect_keys(mode, encrypting)

    try:
        processed, skipped = process_file(
            in_path, out_path, mode, encrypting,
            vkey=vkey, fkey=fkey, key_file=key_file,
        )
        verb = "Encrypted" if encrypting else "Decrypted"
        msg = f"✓ {verb} {processed} line(s) → '{out_path}'"
        if skipped:
            msg += f"  ({skipped} skipped — see warnings above)"
        questionary.print(msg, style="fg:#00bb77 bold")

    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        questionary.print(f"✗ {exc}", style="fg:#ff6b6b bold")


# ── Main menu ─────────────────────────────────────────────────────────────────

_ACTIONS = [
    questionary.Choice("Encrypt",       value="encrypt"),
    questionary.Choice("Decrypt",       value="decrypt"),
    questionary.Choice("Encrypt file",  value="encrypt_file"),
    questionary.Choice("Decrypt file",  value="decrypt_file"),
    questionary.Choice("Keygen",        value="keygen"),
    questionary.Choice("Back",          value="back"),
]


def scrambler_menu() -> None:
    """Entry point called from main.py."""
    questionary.print(
        "\n══ Multi-layer Password Scrambler ══",
        style="fg:#00aabb bold",
    )

    while True:
        action = questionary.select(
            "Action:",
            choices=_ACTIONS,
            pointer="->",
            style=STYLE,
        ).ask()

        if action == "back":
            break
        elif action == "keygen":
            _handle_keygen()
        elif action == "encrypt":
            _handle_single(encrypting=True)
        elif action == "decrypt":
            _handle_single(encrypting=False)
        elif action == "encrypt_file":
            _handle_file(encrypting=True)
        elif action == "decrypt_file":
            _handle_file(encrypting=False)