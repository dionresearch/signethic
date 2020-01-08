import argparse
import os
import stat
import sys

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA


def gen_key_pair(path=None, key_len=1024):
    """gen_key_pair

    Generates a private and public key pair. These will be generated based on the path
    of the private key (the public key will use the same file name plus the extension .pub)

    Alternatively, this can be generated using a tool like openssl:

        openssl genpkey -out signing_key.pem 1024

        openssl rsa -in signing_key.pem -pubout > signing_key.pem.pub

    :param path: a string of the private key file name, with relative or full path
    :param key_len: 1024 bits is default, other lengths can be used like 2048, 4096
    :return:
    """
    if path is None:
        path = "signing_key.pem"
    private_key = RSA.generate(key_len)
    with open(path, "wb") as f:
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        f.write(private_key.exportKey("PEM"))
    public_key = private_key.publickey()
    with open(f"{path}.pub", "wb") as f:
        f.write(public_key.exportKey("PEM"))


def get_private_key(private_key_path=None):
    """get_private_key

    Loads private key. If no path is specified, loads signing_key.pem from the
    current directory.

    :param private_key_path:  a string of the private key file name, with relative or full path
    :return: the private key
    """
    if private_key_path is None:
        private_key_path = "signing_key.pem"

    private_key = None
    with open(private_key_path, "rb") as f:
        private_key = RSA.importKey(f.read())
    return private_key


def get_public_key(public_key_path=None, private_key_path=None):
    """get_public_key

    Loads public key. If no path is specified, loads signing_key.pem.pub from the
    current directory. If a private key path is provided, the public key path is
    ignored and the public key is loaded from the private key.

    :param public_key_path: a string of the public key file name, with relative or full path
    :param private_key_path: a string of the private key file name, with relative or full path
    :return:
    """
    if private_key_path is not None:
        private_key = get_private_key(private_key_path)
        public_key = private_key.publickey().exportKey("PEM")
        return public_key
    elif public_key_path is None:
        public_key_path = "signing_key.pem.pub"
    with open(public_key_path, "rb") as f:
        public_key = RSA.importKey(f.read())
    return public_key


def sign(thing, private_key_path=None):
    """sign

    Creates a digital signature of "thing" using `RSASSA-PKCS1-v1_5`

    :param thing: binary data from any source, or a string
    :param private_key_path: a string of the private key file name, with relative or full path
    :return: the PKCS1 v1.5 signature
    """
    if private_key_path is None:
        private_key_path = "signing_key.pem"
    digest = SHA256.new()
    try:
        digest.update(thing)
    except TypeError:
        digest.update(thing.encode())

    private_key = get_private_key(private_key_path)

    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(digest)
    return signature


def sign_and_persist(thing, path, private_key_path=None):
    """sign_and_persist

    Commit to disk the signature generated by `sign` and the "thing", in one file, specified by the path.

    :param thing: binary data from any source, or a string
    :param path: a string of the resulting file name, with relative or full path (ie. something.zip.signed)
    :param private_key_path: a string of the private key file name, with relative or full path
    :return: the PKCS1 v1.5 signature
    """
    signature = sign(thing, private_key_path)
    with open(path, "wb") as s:
        s.write(signature)
        try:
            s.write(thing)
        except TypeError:
            s.write(thing.encode())
    return signature


def verify(thing, signature, public_key_path=None):
    """verify

    Verify the signature corresponds to the "thing", based on the public key provided. That public key
    has to match the private key that was used to sign. Returns 0 if verification failed.

    :param thing: binary data from any source, or a string
    :param signature: the PKCS1 v1.5 signature previously generated by sign, or loaded from signed file
    :param public_key_path: a string of the public key file name, with relative or full path
    :return: test for True / False on this return value
    """
    if public_key_path is None:
        public_key_path = "signing_key.pem.pub"

    digest = SHA256.new()
    public_key = get_public_key(public_key_path)
    try:
        digest.update(thing)
    except TypeError:
        digest.update(thing.encode())
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, signature)
    return verified


def verify_file(path, public_key_path=None):
    """verify_file

    Loads the signed file and verify the signature and the "thing" match, given a public key.

    :param path: a string of the signed file name, with relative or full path (ie. something.zip.signed)
    :param public_key_path: a string of the public key file name, with relative or full path
    :return: the "thing" in the signed file, or None if signature failed
    """
    with open(path, "rb") as s:
        signature = s.read(128)
        thing = s.read()
    verified = verify(thing, signature, public_key_path)
    if verified == True:
        return thing
    else:
        return None


def main():
    """main

    main entry point, called by command line script signethic.

    Calling signethic with a filename will generate a new file with the .signed extension
    that includes the signature and the file. It will be signed using the key `signing_key.pem`
    in the current directory, unless the SIGNING_KEY environment variable is set.

    Usage:

        signethic

        signethic filename

    To specify signing key, set environment variable, i.e.:

        export SIGNING_KEY=/path/to/key.pem



    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("_", nargs="*")
    args = parser.parse_args()

    private_key_path = os.environ.get("SIGNING_KEY", "signing_key.pem")
    if args._ != []:
        with open(args._[0], "rb") as f:
            thing = f.read()
            output = str(args._[0]) + ".signed"
    else:
        thing = "abcdef"
        output = "test.str.signed"
    if not os.path.exists(private_key_path):
        gen_key_pair(private_key_path)
    signature = sign(thing, private_key_path=private_key_path)
    print(signature)
    signature = sign_and_persist(thing, path=output, private_key_path=private_key_path)
    result = verify(thing, signature, public_key_path=f"{private_key_path}.pub")
    print(f"verify result: {result}")
    result = verify_file(output, public_key_path=f"{private_key_path}.pub")
    if result:
        print(f"{output}: Based on the signature and public key, the payload is intact")
    else:
        print(f"{output}: Payload doesn't match signature")
    return 0


if __name__ == "__main__":
    sys.exit(main())