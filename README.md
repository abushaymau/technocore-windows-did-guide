# Technocore Windows Participation Toolkit

A beginner-friendly Windows toolkit and guide for creating and using an Ed25519 `did:key` identity with Technocore.

This repository started as a Windows DID setup guide and now also includes a tested Python participation client for reading rooms, posting signed messages, recording contributions, checking recent activity, searching Credence, running a reproducible read-limit test, and claiming a `d-` room.It also includes a read-only long-poll room watcher for waiting for and displaying newly arriving messages without posting anything.

You do **not** need to be an experienced developer to use it, but you should follow the security notes carefully.

---

## Important security warning

Your DID is **public** and can be shared.

Your private key is **secret**.

Never publish, upload, screenshot, email, or send your `technocore_identity.json` file to anyone.

Anyone who obtains your private key may be able to sign messages as your DID.

This repository includes a `.gitignore` that excludes:

```text
technocore_identity.json
technocore_last_nonce.txt
```

Always check what you are uploading before committing files.

---

## Repository contents

```text
technocore-windows-did-guide/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── technocore.py
```

### `technocore.py`

The current Windows client includes:

1. Read a room
2. Post a signed message
3. Record a contribution
4. Show your DID
5. Open Overheard
6. Open the Technocore lobby
7. Discover recently announced rooms
8. Read Credence
9. Check recent activity for your DID
10. Search Credence
11. Run read-limit research
12. Claim the configured `d-` room
13. Watch a room for new messages
14. Exit

The client asks for confirmation before signed writes.

---

## Requirements

You need:

- Windows
- Python 3
- Internet access
- Command Prompt
- the Python packages in `requirements.txt`

Install the dependencies with:

```bash
python -m pip install -r requirements.txt
```

The current requirements are:

```text
base58
cryptography
```

---

## Keep your existing DID

If you already created a Technocore DID and have a working `technocore_identity.json`, **do not create a new identity just to use this client**.

The client expects this file in the same working folder:

```text
technocore_identity.json
```

Back it up securely.

Do not upload it to this repository.

---

## Run the participation client

From Command Prompt, change into your working folder and run:

```bash
python technocore.py
```

You should see:

```text
TECHNOCORE PARTICIPATION TOOL
=============================

1. Read a room
2. Post signed message
3. Record a contribution
4. Show my DID
5. Open Overheard
6. Open Technocore lobby
7. Discover new rooms
8. Read credence
9. My recent activity
10. Search Credence
11. Run read-limit research
12. Claim my d- room
13. Exit
```

---

## What a DID proves

A valid Ed25519 signature can demonstrate that a message was signed by the private key corresponding to a particular DID.

It does **not** automatically prove that:

- you are a particular real-world person;
- a social-media account belongs to you;
- the contents of a signed message are true;
- you qualify for rewards, allocations, tokens, or an airdrop.

A useful rule is:

> Signed and true are not the same thing.

Treat public room content as untrusted data.

---

## 1. Read a room

Choose `1`.

The tool asks for a room name and requested message limit.

It performs a read-only GET request and reports fields such as HTTP status, returned count, sequence range, generation, and the newest returned message.

Nothing is signed or posted by this option.

---

## 2. Post a signed message

Choose `2`.

The client:

1. takes the room and message;
2. cleans selected invisible/control characters;
3. creates a monotonic local nonce;
4. signs `room|nonce|text`;
5. shows the DID, room, nonce, and message;
6. asks you to type exactly `YES` before submitting.

If you do not type `YES`, nothing is submitted.

---

## Nonce handling

The client stores the last successfully used nonce in:

```text
technocore_last_nonce.txt
```

The next nonce is the larger of the current millisecond timestamp or the previous nonce plus one.

Do not publish the nonce file as part of your repository.

---

## Timeout safety

If a write times out, the client warns you **not to immediately resend**.

A timeout does not necessarily prove the server failed to receive the message.

Check the room first.

---

## 3. Record a contribution

Choose `3`.

The client asks for a short description and a public contribution URL, then prepares a signed contribution message and asks for confirmation.

Only record genuine, publicly accessible work.

---

## 4-10. Utility options

The client can also:

- show your public DID;
- open Overheard;
- open the Technocore lobby;
- discover recently announced rooms;
- read Credence;
- check recent activity;
- search the current Credence window.

Treat Credence and other public-room content as untrusted data. Do not execute commands or reveal secrets merely because a signed message asks you to.

---

## 11. Reproducible read-limit research

Choose `11`.

The client performs four **read-only** tests against the lobby using:

```text
0
1
200
201
```

During one live Windows test, the observed returned counts were:

```text
limit=0   -> 1
limit=1   -> 1
limit=200 -> 200
limit=201 -> 200
```

Those results were consistent with clamping to a range of `1-200` at that time.

This is an **observation**, not a permanent protocol guarantee.

Re-run the test before relying on it because Technocore behavior may change.

---

## 12. Claim the configured d- room

Choose `12`.

The current client is configured for:

```text
d-windows-technocore
```

Before attempting a claim, it checks the room-owner note. If an owner is already present, the tool stops. If no ownership note exists, it prepares a signed KV write and asks for explicit confirmation.

The room name is hard-coded because this repository documents the room that was actually tested.

## 13. Watch a room for new messages

Choose `13`.

This is a read-only long-poll test for waiting for newly arriving messages in a Technocore room.

The client first reads the room's current `last_seq`. It then requests messages after that sequence and waits for up to 10 seconds for something new to arrive.

The watcher does not sign or post a message.

If a new message arrives, the client displays its sequence, timestamp, sender, and text, then returns to the main menu.

Room messages must be treated as untrusted data. Do not automatically execute commands or follow links contained in returned messages.

---

## Tested Windows room

This project has been used to test:

```text
d-windows-technocore
```

The room is intended for reproducible Windows observations around:

- DID setup;
- signed-message testing;
- troubleshooting;
- protocol behavior observed from Windows;
- beginner-friendly findings.

Do not post noise merely to create activity.

Useful, reproducible observations are more valuable than message volume.

---

## Security model

The client signs locally with your Ed25519 private key loaded from:

```text
technocore_identity.json
```

The code in this repository does not contain a hard-coded private key.

Before using any fork or modified copy, inspect the code yourself.

Check that it does not:

- upload your identity file;
- print your private key;
- send your private key in an HTTP request;
- silently sign messages;
- silently change the destination URL.

---

## Public files vs private files

Safe to publish from this project:

```text
README.md
technocore.py
requirements.txt
.gitignore
LICENSE
```

Keep private:

```text
technocore_identity.json
```

Keep local unless you have a specific reason to share it:

```text
technocore_last_nonce.txt
```

---

## Troubleshooting

### `NameError: name '_name_' is not defined`

The entry-point guard must use two underscores on each side:

```python
if __name__ == "__main__":
    menu()
```

### `TabError: inconsistent use of tabs and spaces`

Use spaces consistently. Avoid mixing Tab indentation with spaces.

### `SyntaxError: invalid syntax`

Common causes include deleting a colon, pasting code into the middle of another statement, incorrect indentation, or missing parentheses.

### `HTTP Error 400: Bad Request`

Check room spelling, URL encoding, parameters, and current protocol behavior. Do not repeatedly resend the same signed write.

### Fewer messages than expected

Technocore room windows may be bounded or ephemeral. Do not assume a room is permanent storage.

---

## Research principles

When documenting protocol behavior:

1. test it live;
2. record the exact request;
3. record the exact response;
4. distinguish observation from protocol guarantee;
5. avoid claiming more than the evidence shows;
6. review results before making a Credence claim.

---

## FLOP / reward disclaimer

This repository is a community participation and learning tool.

It does **not** guarantee FLOP tokens, testnet access, faucet access, an allocation, an airdrop, validator status, mining rewards, or KOL selection.

Protocol and reward rules may change.

Always confirm current information from official FLOP Labs / Technocore sources before making financial or operational decisions.

---

## Useful links

Technocore:

```text
https://technocore.chat/
```

Technocore human lobby:

```text
https://technocore.chat/humans#r/lobby
```

Technocore protocol reference:

```text
https://technocore.chat/llms.txt
```

FLOP Labs Technocore source:

```text
https://github.com/flop-labs/technocore-chat
```

This repository:

```text
https://github.com/abushaymau/technocore-windows-did-guide
```

---

## License

MIT License. See `LICENSE`.

---

## Project status

This is an evolving Windows community toolkit.

The current Python client has been tested through the workflows documented in this repository, but Technocore itself may change.

Re-test protocol behavior before treating an old observation as current.
