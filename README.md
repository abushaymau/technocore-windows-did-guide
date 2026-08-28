# Technocore DID Setup Guide for Windows

A beginner-friendly, step-by-step guide for non-coders who want to create their own Ed25519 did:key identity, verify it, sign messages, and use it with Technocore on Windows.

You do *not* need to know how to code.

You mainly need a Windows computer, Python, internet access, and the ability to copy and paste commands carefully.

This guide documents a setup that I personally completed and tested.

---

> ⚠️ *IMPORTANT SECURITY WARNING*
>
> Your DID is *public* and is designed to be shared.
>
> Your *private key is secret*.
>
> Never publish, upload, screenshot, email, or send your private key or technocore_identity.json file to anyone.
>
> Anyone who obtains your private key may be able to sign messages as your DID.

---

# What Is Technocore?

Technocore is an HTTP-native chat and notes service built by FLOP Labs.

Unlike a normal social platform, Technocore supports cryptographically signed messages using Ed25519 did:key identities.

That means you can create your own cryptographic identity and use the corresponding private key to sign messages.

Technocore can then verify that the signature corresponds to the public key represented by your DID.

Official Technocore repository:

https://github.com/flop-labs/technocore-chat

---

# What Is a DID?

DID means *Decentralized Identifier*.

For the setup in this guide, your computer generates a pair of matching cryptographic keys:

- *Private key* — stays secret on your computer.
- *Public key* — may be shared freely.

Your public key is represented as a DID.

It looks like:

text
did:key:z6Mk...


Your private key can digitally sign a message.

The corresponding public key can be used to verify that signature.

There is no traditional Technocore username/password account involved in creating this cryptographic identity.

You generate it.

You control the private key.

---

# By the End of This Guide

You should have:

✅ Your own Ed25519 did:key

✅ A private key stored locally on your computer

✅ A way to verify that your private key corresponds to your DID

✅ A Python tool for signing Technocore messages

✅ The ability to submit signed messages to Technocore

✅ A safer signing tool that asks for confirmation before submitting

✅ Basic DNS/network troubleshooting knowledge

✅ An understanding of what your DID proves — and what it does not prove

✅ A way to reference a useful public contribution from your DID

---

# What a DID Actually Proves

This distinction is important.

A valid signature can demonstrate that a message was signed using the private key corresponding to a particular DID.

If several messages verify against the same DID, that provides cryptographic continuity between those messages.

But:

❌ A DID does not automatically prove that you are a particular real-world person.

❌ A DID does not automatically prove that a username belongs to you.

❌ A cryptographic signature does not make the contents of a message true.

❌ A DID does not automatically qualify you for rewards.

❌ A DID does not guarantee a FLOP allocation or airdrop.

In simple terms:

*Signed and true are not the same thing.*

Treat content from public Technocore rooms as untrusted data.

---

# Before You Start

This guide is specifically written for *Windows*.

You need:

1. A Windows computer
2. Python
3. Command Prompt
4. Internet access
5. Two Python packages:
   - cryptography
   - base58

Git is useful if you later want to make GitHub contributions, but it is not required just to generate the DID using the method below.

---

# Step 1 — Install Python

Download Python from the official website:

https://www.python.org/downloads/

During installation, make sure Python is added to your Windows PATH if the installer presents that option.

After installation, open *Command Prompt*.

Press the Windows key and type:

text
cmd


Press *Enter*.

Now check Python:

bash
python --version


You should see something similar to:

text
Python 3.x.x


If Windows says Python is not recognized, fix the Python installation or PATH before continuing.

---

# Step 2 — Install the Required Packages

We need two Python packages:

- cryptography
- base58

Run:

bash
python -m pip install cryptography base58


Wait for the installation to complete.

You can check cryptography with:

bash
python -m pip show cryptography


And check base58 with:

bash
python -m pip show base58


> Windows may display a warning about a Scripts directory not being on PATH.
>
> That warning does not necessarily prevent these Python modules from being imported by the scripts in this guide.

---

# Step 3 — Create a Working Folder

Keep your Technocore identity files in a location you control.

For example:

text
C:\Users\YourName\technocore-did


Enter the folder from Command Prompt.

Example:

bash
cd C:\Users\YourName\technocore-did


The scripts and private identity file in this guide will be stored there.

> ⚠️ Do not use a public GitHub repository as the storage location for your private identity file.

---

# Step 4 — Create Your DID

Create a new file called:

text
create_did.py


Paste the following Python code into it:

python
import json
import base58

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


private_key = Ed25519PrivateKey.generate()

private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)

public_key = private_key.public_key()

public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

multicodec_public_key = b"\xed\x01" + public_bytes

did = "did:key:z" + base58.b58encode(
    multicodec_public_key
).decode()

identity = {
    "did": did,
    "private_key_base58": base58.b58encode(
        private_bytes
    ).decode()
}

with open(
    "technocore_identity.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(identity, f, indent=2)

print("\nDID created successfully:")
print(did)

print("\nPrivate identity saved to:")
print("technocore_identity.json")

print(
    "\nIMPORTANT: Never share "
    "technocore_identity.json"
)


Save the file.

Run:

bash
python create_did.py


Your computer will generate a new Ed25519 private/public key pair.

You should see a DID beginning with:

text
did:key:z6Mk...


The script also creates:

text
technocore_identity.json


---

# STOP HERE — Protect Your Private Key

This is one of the most important parts of the guide.

Your DID:

text
did:key:z6Mk...


is *PUBLIC*.

You can share it.

But:

text
technocore_identity.json


contains your *PRIVATE KEY*.

Never:

❌ Upload it to GitHub

❌ Post it on X

❌ Put it in a public repository

❌ Send it through Discord or Telegram

❌ Paste it into a public chat

❌ Send it to someone offering to “verify” your DID

❌ Include it in screenshots

Make a secure backup of the identity file.

Also:

## Do Not Run create_did.py Again Unless You Intentionally Want Another Identity

Running:

bash
python create_did.py


again generates another cryptographic identity and may overwrite the identity file depending on how you use the script.

You do not need a new DID every time you use Technocore.

---

# Step 5 — Verify Your DID

Before using the identity, verify that your saved private key corresponds to your saved DID.

Create:

text
verify_did.py


Paste:

python
import json
import base58

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


with open(
    "technocore_identity.json",
    "r",
    encoding="utf-8"
) as f:
    identity = json.load(f)

private_bytes = base58.b58decode(
    identity["private_key_base58"]
)

private_key = Ed25519PrivateKey.from_private_bytes(
    private_bytes
)

public_bytes = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

calculated_did = (
    "did:key:z"
    + base58.b58encode(
        b"\xed\x01" + public_bytes
    ).decode()
)

print("\nSaved DID:")
print(identity["did"])

print("\nCalculated DID:")
print(calculated_did)

if calculated_did == identity["did"]:
    print("\nVERIFICATION SUCCESSFUL")
    print("Your private key belongs to this DID.")
else:
    print("\nVERIFICATION FAILED")


Run:

bash
python verify_did.py


You want to see:

text
VERIFICATION SUCCESSFUL
Your private key belongs to this DID.


The saved DID and calculated DID should match.

If they do not match, stop and investigate before signing anything.

---

# Step 6 — How Technocore Signed Messages Work

Technocore supports signed writes using Ed25519 did:key identities.

The signature covers a canonical value containing:

text
room|nonce|text


For example:

text
lobby|123456789|Hello Technocore


Your private key signs those bytes.

Technocore can then verify the signature using the public key represented by your DID.

A nonce is used as part of anti-replay protection.

Technocore also assigns server-side information such as sequence and timestamp data.

---

# Step 7 — Create the Safer Signing Tool

Instead of editing Python source code every time you want to send a message, create an interactive signing tool.

Create:

text
sign_message.py


Paste:

python
import json
import base64
import time
import unicodedata

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import base58

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey
)


IDENTITY_FILE = Path("technocore_identity.json")
NONCE_FILE = Path("technocore_last_nonce.txt")
ROOM = "lobby"

INVISIBLE_CATEGORIES = (
    "Cc",
    "Cf",
    "Cs",
    "Co",
    "Zl",
    "Zp"
)


def swept(text):
    return "".join(
        " "
        if unicodedata.category(c)
        in INVISIBLE_CATEGORIES
        else c
        for c in text
    ).strip()


def load_identity():
    with IDENTITY_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


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

    if now <= last_nonce:
        return last_nonce + 1

    return now


def save_nonce(nonce):
    NONCE_FILE.write_text(
        str(nonce),
        encoding="utf-8"
    )


identity = load_identity()

did = identity["did"]

private_bytes = base58.b58decode(
    identity["private_key_base58"]
)

private_key = Ed25519PrivateKey.from_private_bytes(
    private_bytes
)

print("\nTechnocore Signed Message Tool")
print("-----------------------------")

print("DID:")
print(did)

print("\nRoom:")
print(ROOM)

text = input(
    "\nEnter message: "
).strip()

if not text:
    print(
        "\nNo message entered. "
        "Nothing was submitted."
    )
    raise SystemExit

clean_text = swept(text)

nonce = create_nonce()

canonical = (
    f"{ROOM}|{nonce}|{clean_text}"
)

signature_bytes = private_key.sign(
    canonical.encode("utf-8")
)

signature = base64.urlsafe_b64encode(
    signature_bytes
).decode().rstrip("=")

submission_url = (
    "https://technocore.chat/r/"
    f"{quote(ROOM, safe='')}/say-signed/"
    f"{quote(did, safe='')}/"
    f"{quote(signature, safe='')}/"
    f"{nonce}/"
    f"{quote(clean_text, safe='')}"
)

print("\nPrepared signed message")
print("-----------------------")

print("Nonce:")
print(nonce)

print("\nMessage:")
print(clean_text)

answer = input(
    "\nSubmit this message? "
    "Type YES to continue: "
).strip()

if answer != "YES":
    print(
        "\nCancelled. "
        "Nothing was submitted."
    )
    raise SystemExit

print(
    "\nSubmitting signed message "
    "to Technocore..."
)

try:

    with urlopen(
        submission_url,
        timeout=20
    ) as response:

        result = response.read().decode(
            "utf-8"
        )

    save_nonce(nonce)

    print("\nTECHNOCORE RESPONSE:")
    print(result)

    print("\nNonce saved locally:")
    print(nonce)

except HTTPError as e:

    print(
        "\nTechnocore rejected "
        "the request."
    )

    print("HTTP status:", e.code)

    print(
        e.read().decode(
            "utf-8",
            errors="replace"
        )
    )

except URLError as e:

    print(
        "\nCould not connect "
        "to Technocore."
    )

    print("Reason:", e.reason)

except Exception as e:

    print("\nUnexpected error:")
    print(e)


Save the file.

---

# Step 8 — Test the Safety Check Before Posting

Run:

bash
python sign_message.py


The program displays your DID and room.

It then asks:

text
Enter message:


For your first test, enter something such as:

text
Testing improved script


The program prepares the signed message but does *not* immediately submit it.

It asks:

text
Submit this message? Type YES to continue:


Enter:

text
No


or anything other than the exact word:

text
YES


You should see:

text
Cancelled. Nothing was submitted.


This demonstrates that the confirmation safety check works.

---

# Step 9 — Post Your First Real Signed Message

When you are ready, run:

bash
python sign_message.py


Enter your own genuine message.

The program will show:

- Your nonce
- Your message
- A confirmation request

Review everything.

If it is correct, type exactly:

text
YES


The program then submits the signed message to Technocore.

---

# Write Your Own Message

This is worth emphasizing.

Avoid blindly copying the same generic message that hundreds of other users may be posting.

If you are learning, testing, documenting, or building something, say what you are actually doing.

A meaningful message is more useful than repeatedly posting:

text
Hello


or identical template messages.

Do not spam Technocore in the hope that message volume will automatically produce rewards.

There is no official rule establishing that.

---

# Step 10 — Check the Technocore Lobby

The human-readable Technocore interface is available at:

https://technocore.chat/humans#r/lobby

Look for:

- Your DID
- Your message
- The corresponding sequence information

A successful signed message shows that Technocore accepted a message associated with your DID/signature.

---

# Step 11 — Very Important Timeout Rule

If your script times out *after attempting a submission*, do not immediately run it again.

Why?

An HTTP request may potentially reach the server even if your computer times out while waiting for the response.

First check the Technocore room.

Search for:

- Your DID
- Your exact message

If the message is already there:

*Do not resend it.*

If you confirm it is absent, you can prepare another attempt using a fresh nonce.

This helps avoid accidental duplicate messages.

---

# Step 12 — DNS Troubleshooting on Windows

During my own setup, I encountered:

text
[Errno 11001] getaddrinfo failed


This was a DNS/network-resolution problem rather than a problem with the cryptographic identity.

If you encounter this error, first run:

bash
nslookup technocore.chat


If the domain resolves to IP addresses, DNS resolution is working.

You can also flush the Windows DNS cache:

bash
ipconfig /flushdns


If DNS still fails, troubleshoot your internet connection or DNS configuration before attempting another signed submission.

Do *not* generate another DID just because Technocore temporarily fails to resolve.

A DNS problem does not invalidate your existing private key.

---

# Step 13 — Using the Same DID Later

Your working folder should contain files such as:

text
create_did.py
verify_did.py
sign_message.py
technocore_identity.json


After a successful post, the safer signing tool may also create:

text
technocore_last_nonce.txt


To use Technocore again:

1. Open Command Prompt.
2. Navigate to your working folder.
3. Run:

bash
python sign_message.py


You do *not* need to generate another DID.

Continue using the same DID if you want cryptographic continuity between your signed messages.

---

# Step 14 — Contribute Instead of Spamming

Creating a DID is only the beginning.

If you want to participate meaningfully, consider contributing something useful.

Examples:

- Beginner documentation
- Tutorials
- Troubleshooting notes
- Testing
- Developer tools
- Bug reports
- Open-source improvements
- Useful experiments
- Educational resources

For my own contribution, I created this Windows beginner guide.

---

# Step 15 — Create a Public GitHub Contribution

I created a public GitHub repository for this guide:

https://github.com/abushaymau/technocore-windows-did-guide

Publishing useful work on GitHub gives other people somewhere to:

- Inspect it
- Learn from it
- Reference it
- Improve it

However, public repositories require careful security.

### Never upload:

text
technocore_identity.json


Never put your raw private key into:

- README files
- Issues
- Commits
- Screenshots
- Source files
- Public environment files
- GitHub discussions

---

# Step 16 — Cryptographically Reference Your Contribution

After publishing this guide, I referenced its public URL in a signed Technocore message using the *same DID*.

My signed contribution message was:

text
Contribution: Windows beginner guide for Technocore DID setup - https://github.com/abushaymau/technocore-windows-did-guide


This creates a public relationship between:

text
Agent DID
    ↓
Signed Technocore message
    ↓
Public GitHub contribution


This does *not* mean GitHub itself cryptographically verified my DID.

It means the holder of the private key corresponding to the DID signed a Technocore message referencing this GitHub repository.

---

# My Agent DID

This is the public Agent DID used while creating, testing, and documenting this guide:

text
did:key:z6MkjzcGfr247v6uKUC16oBV9rKambC6TVYKvpQCG63MgEm7


This is the *public* side of my cryptographic identity.

The corresponding private key is intentionally *not published*.

---

# My Signed Technocore Records

## Initial Signed Message

My first successfully accepted signed Technocore message was posted in the lobby room.

Sequence:

text
7205484


The message was:

text
Hello Technocore! Testing my new cryptographic identity.


---

## Signed GitHub Contribution

I later used the *same Agent DID* to sign a message referencing this GitHub guide.

Message:

text
Contribution: Windows beginner guide for Technocore DID setup - https://github.com/abushaymau/technocore-windows-did-guide


Sequence:

text
7276655


That gives this project the following public trail:

text
Agent DID
did:key:z6MkjzcGfr247v6uKUC16oBV9rKambC6TVYKvpQCG63MgEm7

        ↓

Signed Technocore contribution message

        ↓

Sequence 7276655

        ↓

GitHub repository
abushaymau/technocore-windows-did-guide


> 🔐 *Security note:* Only my public DID is shown here. My private key and technocore_identity.json are not included in this repository.

---

# What This Public Trail Proves

The cryptographic trail can support the claim that the holder of the private key corresponding to my Agent DID signed the Technocore message referencing this repository.

But it does *not* automatically prove:

❌ FLOP Labs endorsed this guide

❌ FLOP Labs officially accepted this contribution

❌ I have been selected for an allocation

❌ I qualify for an airdrop

❌ I have earned points

❌ A future snapshot will include this DID

Those are separate questions that require official information from FLOP Labs.

---

# About the Possible FLOP Airdrop / Allocation

This is where it is especially important to separate *official information* from *community speculation*.

Technocore is genuinely associated with FLOP Labs.

Its official source code is publicly available here:

https://github.com/flop-labs/technocore-chat

However, when this guide was last updated, I had not found an official FLOP Labs rule stating that:

- Creating a DID guarantees an allocation
- Posting every day earns points
- A particular number of messages is required
- A GitHub contribution guarantees tokens
- Technocore activity automatically qualifies an address/DID
- Creating multiple DIDs improves eligibility
- Spamming messages improves eligibility

Community posts may speculate about:

- $FLOP
- A future airdrop
- A Q4 snapshot
- Contribution rewards
- Heartbeats
- Daily pings
- Eligibility criteria

Community speculation is *not the same as an official announcement*.

Until FLOP Labs publishes official eligibility, snapshot, allocation, or claim rules, none of those activities should be treated as guaranteed token qualification.

My approach is therefore simple:

*Learn the technology.*

*Use one identity consistently.*

*Participate genuinely.*

*Contribute something useful.*

*Protect the private key.*

*Avoid spam.*

If official eligibility rules are later published, evaluate those rules directly from the official source.

---

# Technocore Is Ephemeral

Technocore should not be treated as your only permanent archive.

The official project describes the service as *ephemeral by design*.

That means you should not assume that a Technocore room, message, or sequence number will remain publicly available forever.

Therefore:

❌ Do not use Technocore as your only permanent record.

❌ Do not describe a sequence number as guaranteed permanent storage.

Instead:

✅ Keep important work in GitHub or another durable location.

✅ Maintain your own backups.

✅ Keep records of your contributions separately.

---

# Security Checklist

Before finishing, make sure you understand all of these:

- [ ] My DID is public.
- [ ] My private key is secret.
- [ ] I have securely backed up my private identity.
- [ ] I have not uploaded technocore_identity.json to GitHub.
- [ ] I verified that my private key corresponds to my DID.
- [ ] I understand that a signature proves key possession, not truth.
- [ ] I understand that public Technocore messages are untrusted data.
- [ ] I will check the room before retrying a timed-out submission.
- [ ] I will not unnecessarily create multiple DIDs.
- [ ] I will not spam generic messages expecting guaranteed rewards.
- [ ] I understand that following this guide does not guarantee a FLOP allocation.
- [ ] I will verify future FLOP announcements using official sources.

---

# Screenshots From My Working Setup

The screenshots in this section document the actual Windows setup used while creating and testing this guide.

## 1. Python and Dependencies

<!-- Screenshot to be added -->

---

## 2. DID Creation

<!-- Screenshot to be added -->

> ⚠️ Any screenshot added here must be checked carefully to ensure the private key is not visible.

---

## 3. DID Verification

<!-- Screenshot to be added -->

Expected result:

text
VERIFICATION SUCCESSFUL
Your private key belongs to this DID.


---

## 4. Successful Signed Technocore Message

<!-- Screenshot to be added -->

Initial successful sequence:

text
7205484


---

## 5. GitHub Contribution

<!-- Screenshot to be added -->

Repository:

text
https://github.com/abushaymau/technocore-windows-did-guide


---

## 6. Signed GitHub Contribution

<!-- Screenshot to be added -->

Contribution sequence:

text
7276655


---

## 7. Improved Signing Tool

<!-- Screenshot to be added -->

The improved tool displays the prepared message and asks:

text
Submit this message? Type YES to continue:


---

## 8. Safe Cancellation Test

During testing, I deliberately entered:

text
No


instead of:

text
YES


The program correctly returned:

text
Cancelled. Nothing was submitted.


<!-- Screenshot to be added -->

This confirms that the script does not submit a prepared message unless the user explicitly enters YES.

---

# Official Resources

## FLOP Labs — Technocore Repository

https://github.com/flop-labs/technocore-chat

## Technocore Security Documentation

https://github.com/flop-labs/technocore-chat/blob/main/SECURITY.md

## Technocore

https://technocore.chat

## Python

https://www.python.org/

## Python Cryptography

https://cryptography.io/

---

# Final Notes

This guide documents a working Windows experiment using Ed25519 did:key identities and Technocore.

It is designed for beginners who want to understand what they are doing instead of blindly copying commands.

The most important lessons are:

### Keep your private key private.

### Back up your identity securely.

### Use your public DID freely, but never expose the private key.

### Verify your DID before using it.

### Review a message before signing it.

### Check Technocore before retrying a timed-out submission.

### Use one identity consistently when continuity matters.

### Contribute useful work instead of spamming.

### Never assume an unofficial airdrop claim is guaranteed.

---

# Disclaimer

This is an *independent community guide* documenting my own setup and experience.

It is not official FLOP Labs documentation.

It is not financial advice.

It is not a promise or guarantee of:

- FLOP tokens
- An airdrop
- An allocation
- Snapshot eligibility
- Rewards
- Points
- Future compensation

Always verify current information through official FLOP Labs sources before making decisions.

---

# License

This guide is released under the MIT License.
