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

url = "https://twig.ct.letsencrypt.org/2024h1/ct/v1/add-chain"

# python-dotenv, bot3, gzip, json, ratelimit

PROCESSED_CHAINS_FILE = "processed_files.txt"
directory = "OONI-S3-Datasets/2024"

def is_chain_processed(chain):
    try:
        chain_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        for cert in chain:
            chain_hash.update(cert.public_bytes(serialization.Encoding.DER))
        chain_hash = chain_hash.finalize().hex()

        with open(PROCESSED_CHAINS_FILE, 'r') as f:
            return chain_hash in f.read().splitlines()
    except FileNotFoundError:
        return False

def mark_chain_processed(chain):
    chain_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    for cert in chain:
        chain_hash.update(cert.public_bytes(serialization.Encoding.DER))
    chain_hash = chain_hash.finalize().hex()

    with open(PROCESSED_CHAINS_FILE, 'a') as f:
        f.write(chain_hash + '\n')

def fetch_measurement_data(file_path):
    try:
        with gzip.open(file_path, 'rb') as f:
            for line in f:
                try:
                    measurement_data = json.loads(line.decode('utf-8'))
                    yield measurement_data 
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
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl.gz"):
            file_path = os.path.join(directory, filename)
            try:
                for measurement in fetch_measurement_data(file_path):  # Iterate over each measurement in the file
                    if measurement:
                        certificate_chains = extract_certificate_chains(measurement)
                        if certificate_chains:
                            for chain in certificate_chains:
                                if not is_chain_processed(chain):
                                    submit_to_ct(chain)
                                    mark_chain_processed(chain)
                                else:
                                    print(f"Skipping already submitted chain in {filename}")
                        else:
                            print(f"No certificate chains found in {filename}")
                    else:
                        print(f"No valid measurement data found in {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
        else:
            print(f"Skipping non-JSONL file: {filename}")