import json
import gzip
import os
import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import binascii
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography import x509
import datetime
from ratelimit import limits
import time


url = "https://twig.ct.letsencrypt.org/2024h1/ct/v1/add-chain"

# python-dotenv, bot3, gzip, json, ratelimit

PROCESSED_FILES_FILE = "processed_files.txt"
directory = "OONI-S3-Datasets/2024"

def is_file_processed(file_path):
    try:
        with open(PROCESSED_FILES_FILE, 'r') as f:
            return file_path in f.read().splitlines()
    except FileNotFoundError:
        return False

def mark_file_processed(file_path):
    """Marks a file as processed."""
    with open(PROCESSED_FILES_FILE, 'a') as f:
        f.write(file_path + '\n')

def fetch_measurement_data(file_path):
    try:
        with gzip.open(file_path, 'rb') as f:
            for line in f:
                try:
                    measurement_data = json.loads(line.decode('utf-8'))
                    return measurement_data 
                except json.JSONDecodeError as e:
                    print(f"Failed to decode line: {e}")
    except Exception as e:
        print(f"Failed to read file: {e}")

@limits(calls=3, period=10)
def submit_to_ct(chain):
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
    try:
        if measurement_data.get("test_name") != "web_connectivity":
            return []

        tls_handshakes = measurement_data.get('test_keys', {}).get('tls_handshakes', [])

        if not tls_handshakes:
            print("No tls_handshakes found in measurement data.")
            return []

        all_certs = []

        for tls_handshake in tls_handshakes:
           peer_certificates = tls_handshake.get('peer_certificates', [])  # Extract the certificate chain
            # Parse Certificate Chains
           certs = []
           for cert_data in peer_certificates:
                cert_bytes = base64.b64decode(cert_data['data'])
                try:
                    cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
                    certs.append(cert)
                except ValueError:
                    print(f"Failed to decode certificate in chain: {cert_data['data']}")
            
           if certs: # If the cert list is not empty
                all_certs.append(certs)  # Add it to the list of all certificate chains

        return all_certs 

    except Exception as e:
        print(f"Error extracting certificate chain: {e}")
        return []

if __name__ == "__main__":
    file_count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl.gz"):
            file_path = os.path.join(directory, filename)
            
            # Check if the file has been processed
            if not is_file_processed(file_path):
                measurement_data = fetch_measurement_data(file_path)

                if measurement_data:
                    certificate_chains = extract_certificate_chains(measurement_data)

                    if certificate_chains:
                        print(f"Processing {filename}:")

                        for chain in certificate_chains:
                            time.sleep(2)
                            submit_to_ct(chain)

                    else:
                        print(f"No certificate chains found in {filename}")

                else:
                    print(f"Failed to fetch measurement data from {filename}")
            else:
                print(f"Skipping already processed file: {filename}")

            mark_file_processed(file_path)  # Mark file as processed

            file_count += 1

            if file_count >= 5:
                       break  # Early stopping for testing
        else:
            print(f"Skipping non-JSONL file: {filename}")