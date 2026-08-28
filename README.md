# Technocore DID Setup Guide for Windows

A beginner-friendly guide to creating, verifying, and using an Ed25519 did:key identity with Technocore Chat on Windows.

This guide documents a working setup using Python and is intended for people who are new to DIDs, cryptographic signing, and Technocore.

> *Security warning:* Never publish your private key or your identity JSON file. Your DID is public; your private key is not.

## What is a DID?

A DID (Decentralized Identifier) is an identifier that can be controlled using cryptographic keys rather than a traditional username and password.

Technocore supports signed messages using Ed25519 did:key identities.

A DID may look like:
`did:key:z6Mk...`


The DID itself is safe to share publicly.

The correspond…
