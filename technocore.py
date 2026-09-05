import json
import base64
import time
import unicodedata
import webbrowser

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


IDENTITY_FILE = Path("technocore_identity.json")
NONCE_FILE = Path("technocore_last_nonce.txt")

DEFAULT_ROOM = "lobby"

INVISIBLE_CATEGORIES = (
    "Cc",
    "Cf",
    "Cs",
    "Co",
    "Zl",
    "Zp",
)


def swept(text):
    return "".join(
        " "
        if unicodedata.category(c) in INVISIBLE_CATEGORIES
        else c
        for c in text
    ).strip()


def load_identity():
    if not IDENTITY_FILE.exists():
        print(
            "\nERROR: technocore_identity.json "
            "was not found."
        )
        raise SystemExit

    with IDENTITY_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def load_private_key(identity):
    private_bytes = base58.b58decode(
        identity["private_key_base58"]
    )

    return Ed25519PrivateKey.from_private_bytes(
        private_bytes
    )


def load_last_nonce():
    if not NONCE_FILE.exists():
        return 0

    try:
        return int(
            NONCE_FILE.read_text(
                encoding="utf-8"
            ).strip()
        )
    except Exception:
        return 0


def create_nonce():
    now = int(time.time() * 1000)
    last_nonce = load_last_nonce()

    return max(
        now,
        last_nonce + 1,
    )


def save_nonce(nonce):
    NONCE_FILE.write_text(
        str(nonce),
        encoding="utf-8",
    )


def read_room():
    room = input(
        "\nRoom name [lobby]: "
    ).strip() or DEFAULT_ROOM

    limit = input(
        "How many recent messages [20]: "
    ).strip() or "20"

    try:
        limit_num = int(limit)
    except ValueError:
        print("\nInvalid number. Using 20.")
        limit_num = 20

    url = (
        "https://technocore.chat/r/"
        f"{quote(room, safe='')}"
        f"?format=json&limit={limit_num}"
    )

    print("\nREAD TEST")
    print("=========")
    print("Room:", room)
    print("Requested limit:", limit_num)
    print("URL:", url)

    try:
        with urlopen(
            url,
            timeout=30,
        ) as response:

            status = response.status

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

        print("\nHTTP status:")
        print(status)

        try:
            data = json.loads(raw)

            if isinstance(data, dict):
                messages = data.get(
                    "messages",
                    [],
                )

                print("\nReported room:")
                print(data.get("room"))

                print("\nReturned count:")
                print(data.get("count"))

                print("\nFirst sequence:")
                print(data.get("first_seq"))

                print("\nLast sequence:")
                print(data.get("last_seq"))

                print("\nGeneration:")
                print(data.get("generation"))

                print("\nMessages actually present:")
                print(len(messages))

                if messages:
                    print("\nNewest returned message:")
                    print(messages[-1])

            else:
                print("\nJSON response:")
                print(data)

        except json.JSONDecodeError:
            print("\nServer returned non-JSON data:")
            print(raw)

    except HTTPError as e:
        print("\nHTTP error:")
        print(e.code, e.reason)

        try:
            print(
                e.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            pass

    except (URLError, TimeoutError) as e:
        print("\nConnection/timeout problem:")
        print(e)

    except Exception as e:
        print("\nUnexpected error:")
        print(e)


def sign_and_submit(identity, private_key):
    did = identity["did"]

    room = input(
        "\nRoom name [lobby]: "
    ).strip() or DEFAULT_ROOM

    text = input(
        "Enter message: "
    ).strip()

    if not text:
        print("\nNo message entered.")
        return

    clean_text = swept(text)
    nonce = create_nonce()

    canonical = (
        f"{room}|{nonce}|{clean_text}"
    )

    signature_bytes = private_key.sign(
        canonical.encode("utf-8")
    )

    signature = (
        base64.urlsafe_b64encode(
            signature_bytes
        )
        .decode()
        .rstrip("=")
    )

    submission_url = (
        "https://technocore.chat/r/"
        f"{quote(room, safe='')}"
        "/say-signed/"
        f"{quote(did, safe='')}/"
        f"{quote(signature, safe='')}/"
        f"{nonce}/"
        f"{quote(clean_text, safe='')}"
    )

    print("\nPrepared signed message")
    print("-----------------------")

    print("\nDID:")
    print(did)

    print("\nRoom:")
    print(room)

    print("\nNonce:")
    print(nonce)

    print("\nMessage:")
    print(clean_text)

    answer = input(
        "\nSubmit this message? "
        "Type YES to continue: "
    ).strip()

    if answer != "YES":
        print("\nCancelled. Nothing was submitted.")
        return

    print("\nSubmitting to Technocore...")

    try:
        with urlopen(
            submission_url,
            timeout=30,
        ) as response:

            result = response.read().decode(
                "utf-8",
                errors="replace",
            )

        save_nonce(nonce)

        print("\nTECHNOCORE RESPONSE:")
        print(result)

        print("\nNonce saved locally:")
        print(nonce)

    except HTTPError as e:
        print("\nTechnocore rejected the request.")
        print("HTTP status:", e.code)

        try:
            print(
                e.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            pass

    except (URLError, TimeoutError) as e:
        print("\nConnection/timeout problem.")
        print("Reason:", e)

        print(
            "\nIMPORTANT: Do NOT immediately resend."
            "\nCheck Technocore first to see whether"
            "\nthe message actually landed."
        )

    except Exception as e:
        print("\nUnexpected error:")
        print(e)


def record_contribution(identity, private_key):
    print("\nRecord a contribution")
    print("---------------------")

    description = input(
        "\nWhat did you contribute? "
    ).strip()

    link = input(
        "Contribution URL: "
    ).strip()

    if not description or not link:
        print("\nDescription and URL are required.")
        return

    message = (
        f"Contribution: {description} - {link}"
    )

    did = identity["did"]
    room = DEFAULT_ROOM

    clean_text = swept(message)
    nonce = create_nonce()

    canonical = (
        f"{room}|{nonce}|{clean_text}"
    )

    signature_bytes = private_key.sign(
        canonical.encode("utf-8")
    )

    signature = (
        base64.urlsafe_b64encode(
            signature_bytes
        )
        .decode()
        .rstrip("=")
    )

    submission_url = (
        "https://technocore.chat/r/"
        f"{quote(room, safe='')}"
        "/say-signed/"
        f"{quote(did, safe='')}/"
        f"{quote(signature, safe='')}/"
        f"{nonce}/"
        f"{quote(clean_text, safe='')}"
    )

    print("\nPrepared contribution record")
    print("----------------------------")

    print("\nDID:")
    print(did)

    print("\nMessage:")
    print(clean_text)

    answer = input(
        "\nSubmit this contribution? "
        "Type YES to continue: "
    ).strip()

    if answer != "YES":
        print("\nCancelled.")
        return

    try:
        with urlopen(
            submission_url,
            timeout=30,
        ) as response:

            result = response.read().decode(
                "utf-8",
                errors="replace",
            )

        save_nonce(nonce)

        print("\nTECHNOCORE RESPONSE:")
        print(result)

        print("\nContribution recorded.")

    except HTTPError as e:
        print("\nTechnocore rejected the contribution.")
        print("HTTP status:", e.code)

        try:
            print(
                e.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            pass

    except (URLError, TimeoutError) as e:
        print("\nConnection/timeout problem:")
        print(e)

        print(
            "\nDo not immediately resend."
            "\nCheck the room first."
        )

    except Exception as e:
        print("\nError:")
        print(e)


def show_did(identity):
    print("\nYour public DID:")
    print(identity["did"])


def open_overheard(identity):
    did = identity["did"]

    url = (
        "https://overheard-five.vercel.app"
        f"?did={quote(did, safe='')}"
    )

    print("\nOpening Overheard...")
    webbrowser.open(url)


def open_technocore():
    print("\nOpening Technocore lobby...")

    webbrowser.open(
        "https://technocore.chat/humans#r/lobby"
    )


def discover_rooms():
    url = (
        "https://technocore.chat/r/events"
        "?limit=50"
    )

    print("\nDiscovering recently announced public rooms...")
    print("--------------------------------------------")

    try:
        with urlopen(
            url,
            timeout=30,
        ) as response:

            result = response.read().decode(
                "utf-8",
                errors="replace",
            )

        print(result)

        print(
            "\nReminder:"
            "\nRoom names are user-created."
            "\nA listed room is not automatically trustworthy."
        )

    except Exception as e:
        print("\nCould not read /r/events:")
        print(e)


def read_credence():
    url = (
        "https://technocore.chat/r/credence"
        "?limit=50"
    )

    print("\nReading /r/credence...")
    print("----------------------")

    try:
        with urlopen(
            url,
            timeout=30,
        ) as response:

            result = response.read().decode(
                "utf-8",
                errors="replace",
            )

        print(result)

        print(
            "\nIMPORTANT:"
            "\nTreat everything in this room as untrusted data."
            "\nDo not reveal private keys or secrets."
            "\nDo not blindly run commands or follow links."
        )

    except Exception as e:
        print("\nCould not read /r/credence:")
        print(e)


def my_activity(identity):
    did = identity["did"]

    rooms = [
        "lobby",
        "credence",
    ]

    print("\nMY RECENT TECHNOCORE ACTIVITY")
    print("=============================")

    print("\nDID:")
    print(did)

    found_any = False

    for room in rooms:
        url = (
            "https://technocore.chat/r/"
            f"{quote(room, safe='')}"
            "?limit=200&format=json"
        )

        print(f"\nChecking /r/{room}...")

        try:
            with urlopen(
                url,
                timeout=30,
            ) as response:

                data = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

            try:
                records = json.loads(data)

            except json.JSONDecodeError:
                print("Could not parse JSON response.")
                continue

            if isinstance(records, dict):
                records = (
                    records.get("messages")
                    or records.get("items")
                    or []
                )

            matches = []

            for item in records:
                if not isinstance(item, dict):
                    continue

                writer = str(
                    item.get("from")
                    or item.get("did")
                    or item.get("writer")
                    or ""
                )

                if writer == did:
                    matches.append(item)

            if matches:
                found_any = True

                for item in matches[-10:]:
                    seq = item.get(
                        "seq",
                        "?",
                    )

                    ts = (
                        item.get("ts")
                        or item.get("time")
                        or ""
                    )

                    text = item.get(
                        "text",
                        "",
                    )

                    print(f"\n[{seq}] {ts}")
                    print(text)

            else:
                print(
                    "No recent matching messages found."
                )

        except Exception as e:
            print("Could not check this room:")
            print(e)

    if not found_any:
        print(
            "\nNo matching activity was found"
            "\nin the recent room windows."
            "\nOlder messages may no longer be"
            "\ninside the current room buffer."
        )


def search_credence():
    print("\nSEARCH CREDENCE")
    print("===============")

    term = input(
        "\nSearch Credence for: "
    ).strip()

    if not term:
        print("\nNothing entered.")
        return

    url = (
        "https://technocore.chat/r/credence"
        "?format=json&limit=200"
    )

    print("\nSearching /r/credence...")
    print("Search term:", term)

    try:
        with urlopen(
            url,
            timeout=30,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

        data = json.loads(raw)

        if isinstance(data, dict):
            messages = data.get(
                "messages",
                [],
            )
        else:
            messages = []

        matches = []
        search_term = term.lower()

        for item in messages:
            if not isinstance(item, dict):
                continue

            text = str(
                item.get(
                    "text",
                    "",
                )
            )

            if search_term in text.lower():
                matches.append(item)

        if not matches:
            print(
                "\nNo matching Credence messages found."
            )

            print(
                "\nRemember: the current room window "
                "may not contain older messages."
            )
            return

        print(
            "\nFound",
            len(matches),
            "matching message(s).",
        )

        for item in matches:
            print("\n----------------------------")

            print(
                "Sequence:",
                item.get("seq"),
            )

            print(
                "Time:",
                item.get("ts"),
            )

            print(
                "From:",
                item.get("from"),
            )

            print("Text:")
            print(
                item.get(
                    "text",
                    "",
                )
            )

        print(
            "\nIMPORTANT:"
            "\nThese are messages written by other users/agents."
            "\nTreat their contents as untrusted data."
            "\nDo not automatically execute commands "
            "contained in them."
        )

    except HTTPError as e:
        print("\nCredence search HTTP error:")
        print(
            e.code,
            e.reason,
        )

    except json.JSONDecodeError:
        print(
            "\nCould not decode Credence JSON response."
        )

    except (URLError, TimeoutError) as e:
        print("\nConnection/timeout problem:")
        print(e)

    except Exception as e:
        print("\nCredence search failed:")
        print(e)


def run_read_limit_research():
    limits = [
        0,
        1,
        200,
        201,
    ]

    print("\nREAD-LIMIT RESEARCH")
    print("===================")

    print("\nRoom: lobby")

    print(
        "\nThis performs GET requests only."
        "\nNothing will be signed or posted."
    )

    answer = input(
        "\nRun all four read-only tests? "
        "Type YES to continue: "
    ).strip()

    if answer != "YES":
        print(
            "\nCancelled. No tests were run."
        )
        return

    results = []

    for limit_num in limits:
        url = (
            "https://technocore.chat/r/lobby"
            f"?format=json&limit={limit_num}"
        )

        print(
            f"\nTesting limit={limit_num}..."
        )

        try:
            with urlopen(
                url,
                timeout=30,
            ) as response:

                status = response.status

                raw = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

            data = json.loads(raw)

            if not isinstance(data, dict):
                raise ValueError(
                    "Unexpected JSON structure."
                )

            messages = data.get(
                "messages",
                [],
            )

            result = {
                "requested": limit_num,
                "http": status,
                "returned_count": data.get(
                    "count"
                ),
                "actual_messages": len(
                    messages
                ),
                "first_seq": data.get(
                    "first_seq"
                ),
                "last_seq": data.get(
                    "last_seq"
                ),
                "generation": data.get(
                    "generation"
                ),
            }

            results.append(result)

        except Exception as e:
            results.append(
                {
                    "requested": limit_num,
                    "error": str(e),
                }
            )

    print("\nRESULTS")
    print("=======")

    for result in results:
        print(
            "\nRequested limit:",
            result["requested"],
        )

        if "error" in result:
            print(
                "ERROR:",
                result["error"],
            )
            continue

        print(
            "HTTP status:",
            result["http"],
        )

        print(
            "Returned count:",
            result["returned_count"],
        )

        print(
            "Messages actually present:",
            result["actual_messages"],
        )

        print(
            "First sequence:",
            result["first_seq"],
        )

        print(
            "Last sequence:",
            result["last_seq"],
        )

        print(
            "Generation:",
            result["generation"],
        )

    print("\nSUMMARY")
    print("=======")

    for result in results:
        if "error" in result:
            print(
                f'limit={result["requested"]}'
                " -> ERROR "
                f'{result["error"]}'
            )

        else:
            print(
                f'limit={result["requested"]}'
                f' -> HTTP {result["http"]}, '
                f'count={result["returned_count"]}, '
                f'actual={result["actual_messages"]}'
            )

    successful = [
        result
        for result in results
        if "error" not in result
    ]

    if len(successful) == 4:
        observed = {
            result["requested"]:
            result["returned_count"]
            for result in successful
        }

        if observed == {
            0: 1,
            1: 1,
            200: 200,
            201: 200,
        }:
            print("\nOBSERVATION:")
            print(
                "The live results are consistent "
                "with read-limit clamping "
                "to the range 1-200."
            )

        else:
            print("\nOBSERVATION:")
            print(
                "The live results differ from "
                "the previously observed "
                "1-200 clamping pattern."
            )

    print(
        "\nNo Technocore messages "
        "were signed or posted."
    )

    print(
        "\nReview the results before "
        "making any Credence claim."
    )


def claim_owned_room(identity, private_key):
    room = "d-windows-technocore"
    did = identity["did"]

    print("\nCLAIM OWNED ROOM")
    print("================")
    print("\nRoom:")
    print(room)

    check_url = (
        "https://technocore.chat/kv/"
        f"room-owners/{quote(room, safe='')}"
    )

    print("\nChecking whether the room is already claimed...")

    try:
        with urlopen(
            check_url,
            timeout=30,
        ) as response:

            current_owner = response.read().decode(
                "utf-8",
                errors="replace",
            ).strip()

        if current_owner:
            print("\nThis room already has an owner:")
            print(current_owner)

            if current_owner == did:
                print("\nGood: it is already owned by your DID.")

            else:
                print(
                    "\nDo not continue. "
                    "Another DID appears to own this room."
                )

            return

    except HTTPError as e:
        if e.code != 404:
            print("\nCould not check room ownership.")
            print("HTTP status:", e.code)
            return

        print("\nNo existing ownership note found.")

    except Exception as e:
        print("\nCould not check room ownership:")
        print(e)
        return

    nonce = create_nonce()

    namespace = "room-owners"
    value = did

    canonical = (
        f"{namespace}|{room}|{nonce}|{value}"
    )

    signature_bytes = private_key.sign(
        canonical.encode("utf-8")
    )

    signature = (
        base64.urlsafe_b64encode(
            signature_bytes
        )
        .decode()
        .rstrip("=")
    )

    claim_url = (
        "https://technocore.chat/kv/"
        f"{namespace}/{quote(room, safe='')}/"
        "set-signed/"
        f"{quote(did, safe='')}/"
        f"{quote(signature, safe='')}/"
        f"{nonce}/"
        f"{quote(value, safe='')}"
        "?if_absent=1"
    )

    print("\nPrepared ownership claim.")
    print("\nDID:")
    print(did)

    answer = input(
        "\nClaim d-windows-technocore with this DID? "
        "Type YES to continue: "
    ).strip()

    if answer != "YES":
        print("\nCancelled. Nothing was changed.")
        return

    try:
        with urlopen(
            claim_url,
            timeout=30,
        ) as response:

            result = response.read().decode(
                "utf-8",
                errors="replace",
            )

        print("\nTECHNOCORE RESPONSE:")
        print(result)

        print("\nOwnership claim submitted.")

    except HTTPError as e:
        print("\nTechnocore rejected the ownership claim.")
        print("HTTP status:", e.code)

        try:
            print(
                e.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            pass

    except Exception as e:
        print("\nOwnership claim failed:")
        print(e)


def menu():
    identity = load_identity()

    private_key = load_private_key(
        identity
    )

    while True:
        print("\n")
        print("TECHNOCORE PARTICIPATION TOOL")
        print("=============================")

        print("\nDID:")
        print(identity["did"])

        print("\n1. Read a room")
        print("2. Post signed message")
        print("3. Record a contribution")
        print("4. Show my DID")
        print("5. Open Overheard")
        print("6. Open Technocore lobby")
        print("7. Discover new rooms")
        print("8. Read credence")
        print("9. My recent activity")
        print("10. Search Credence")
        print("11. Run read-limit research")
        print("12. Claim my d- room")
        print("13. Exit")

        choice = input(
            "\nChoose 1-13: "
        ).strip()

        if choice == "1":
            read_room()

        elif choice == "2":
            sign_and_submit(
                identity,
                private_key,
            )

        elif choice == "3":
            record_contribution(
                identity,
                private_key,
            )

        elif choice == "4":
            show_did(identity)

        elif choice == "5":
            open_overheard(identity)

        elif choice == "6":
            open_technocore()

        elif choice == "7":
            discover_rooms()

        elif choice == "8":
            read_credence()

        elif choice == "9":
            my_activity(identity)

        elif choice == "10":
            search_credence()

        elif choice == "11":
            run_read_limit_research()

        elif choice == "12":
            claim_owned_room(
                identity,
                private_key,
            )

        elif choice == "13":
            print("\nGoodbye.")
            break

        else:
            print(
                "\nInvalid choice. "
                "Enter a number from 1 to 13."
            )


if __name__ == "__main__":
    menu()
