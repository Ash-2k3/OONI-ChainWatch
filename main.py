import json
import gzip
import os
import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend


# python-dotenv, bot3, gzip, json

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
    # Directory where JSONL files are stored
    directory = "OONI-S3-Datasets"
    
    # Iterate through JSONL files in the local directory
    file_count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl.gz"):
            file_path = os.path.join(directory, filename)
            measurement_data = fetch_measurement_data(file_path)

            if measurement_data:
                # Process measurement data to extract certificate chains
                certificate_chains = extract_certificate_chains(measurement_data)
                print("Certificate Chains: ")
                print(certificate_chains)
                file_count += 1

                if file_count >= 8:
                           break
            else:
                print("Failed to fetch measurement data.")