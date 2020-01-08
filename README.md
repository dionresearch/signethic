# Signethic

A Python module to easily and quickly cryptographically sign a "thing". The
"thing" in question can be anything like a string, or any binary sequence. The
binary sequence could be the output of a serializer, pickling, shelving, compiled
code, encoder, compression or pretty much anything else. The digital signature
based on Public-Key Cryptography Standards (PKCS) prevents tampering.

Note that this is not doing any encryption, only signing. This protects the
"thing" from manipulation, but not from reading. Your overall cybersecurity
strategy should also cover encryption at rest, encryption in flight and least
privileges, along with all the other best practices in this area.

# Installation

## From source

    python setup.py install


## From pypi

    pip install signethic


# Quickstart

Signing a "thing" and saving to a binary file that will contain the digital
signature (PKCS) and the "thing". In this case, a string:

```python
from signetic import sign_and_persist


thing = "the result of our campaign #12345 resulted in sales of $54321.00"

signature = sign_and_persist(thing, path="result.signed")
```

Verifying a file that has been signed, returning the "thing" if the signature
is verified:

```python
from signetic import verify_file

public_key = ...

thing = verify_file("result.signed", public_key)
```


# Command Line

After installing signethic, a command line is available. With no argument, it
will generate a private and public key, create a string, sign it, verify it, save
a binary file with the signature and string and verify that file. (*see* `main()`
for the details of the steps).

Calling signethic with a filename will generate a new file with the .signed extension
that includes the signature and the file. It will be signed using the key `signing_key.pem`
in the current directory, by default. To specify a different signing key, use an environment
variable:

    export SIGNING_KEY=/path/to/key.pem
    
