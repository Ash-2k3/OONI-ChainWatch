import json
import gzip
import os
import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from ratelimit import limits
import time
import boto3
from dotenv import load_dotenv
import io

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "ooni-data-eu-fra"
PREFIX = "raw/20240101/00/CH/webconnectivity"

url = "https://twig.ct.letsencrypt.org/2024h1/ct/v1/add-chain"

# python-dotenv, bot3, gzip, json, ratelimit

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name='eu-central-1')

PROCESSED_CHAINS_FILE = "processed_chains.txt"
directory = "OONI-S3-Datasets/2024"


def is_chain_processed(chain):
    """Checks if a certificate chain has already been processed by calculating its SHA256 hash and comparing it to the ones stored in the processed chains file."""
    try:
        chain_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        for cert in chain:
            chain_hash.update(cert.public_bytes(serialization.Encoding.DER))
        chain_hash = chain_hash.finalize().hex()

        with open(PROCESSED_CHAINS_FILE, "r") as f:
            return chain_hash in f.read().splitlines()
    except FileNotFoundError:
        return False


def mark_chain_processed(chain):
    """Marks a certificate chain as processed by calculating its SHA256 hash and storing it in the processed chains file."""
    chain_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    for cert in chain:
        chain_hash.update(cert.public_bytes(serialization.Encoding.DER))
    chain_hash = chain_hash.finalize().hex()

    with open(PROCESSED_CHAINS_FILE, "a") as f:
        f.write(chain_hash + "\n")


@limits(calls=3, period=10)
def submit_to_ct(chain):
    """Submits a certificate chain to the specified CT log with rate limiting."""
    chain_data = [cert.public_bytes(serialization.Encoding.DER) for cert in chain]
    payload = {"chain": [base64.b64encode(data).decode() for data in chain_data]}

    try:
        response = requests.post(url, json=payload)
        # Handle various response codes
        if response.status_code == 200:
            print(f"Submission successful: {response.json()}")
        elif 400 <= response.status_code < 500:
            print(f"Client error: {response.status_code}, {response.text}")
        elif response.status_code >= 500:
            print(f"Server error: {response.status_code}, {response.text}")
        else:
            print(f"Unexpected response: {response.status_code}, {response.text}")

    except requests.exceptions.RequestException as err:
        print(f"Error submitting chain: {err}")


def extract_certificate_chains(measurement_data):
    """Extracts and parses certificate chains from OONI web connectivity measurement data."""
    try:
        if measurement_data.get("test_name") != "web_connectivity":
            return []

        tls_handshakes = measurement_data.get("test_keys", {}).get("tls_handshakes", [])

        if not tls_handshakes:
            print("No tls_handshakes found in measurement data.")
            return []

        all_certs = []

        for tls_handshake in tls_handshakes:
            peer_certificates = tls_handshake.get(
                "peer_certificates", []
            )  # Extract the certificate chain
            # Parse Certificate Chains
            certs = []
            for cert_data in peer_certificates:
                cert_bytes = base64.b64decode(cert_data["data"])
                try:
                    cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
                    certs.append(cert)
                except ValueError:
                    print(f"Failed to decode certificate in chain: {cert_data['data']}")

            if certs:  # If the cert list is not empty
                all_certs.append(certs)  # Add it to the list of all certificate chains

        return all_certs

    except Exception as e:
        print(f"Error extracting certificate chain: {e}")
        return []


if __name__ == "__main__":
    try:
        # List objects in S3 bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
        if "Contents" in response:
            print('         Contents is indeed in response')
            for obj in response["Contents"]:
                key = obj["Key"]
                print(f"Downloading {key}...")
                # Download object data
                obj_data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                body = obj_data["Body"].read()
                # Parse gzip data
                with gzip.GzipFile(fileobj=io.BytesIO(body), mode="rb") as f:
                    for line in f:
                        measurement_data = json.loads(line.decode("utf-8"))
                        certificate_chains = extract_certificate_chains(measurement_data)
                        if certificate_chains:
                            for chain in certificate_chains:
                                if not is_chain_processed(chain):
                                    time.sleep(5)
                                    submit_to_ct(chain)
                                    mark_chain_processed(chain)
                print(f"Finished processing {key}")
        else:
            print("No objects found in the specified prefix.")
    except Exception as e:
        print(f"Error: {e}")
