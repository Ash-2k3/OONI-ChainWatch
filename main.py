import json
import gzip
import os
import requests
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# python-dotenv, bot3, gzip, json

def fetch_measurements(test_name="web_connectivity", limit=5):
    url = f"https://api.ooni.io/api/v1/measurements?test_name={test_name}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        measurements = response.json()["results"]
        return measurements
    else:
        print(f"Failed to fetch measurements. Status code: {response.status_code}")
        return []

def fetch_measurement_data(measurement_url): # Raw measurement data
    response = requests.get(measurement_url)
    if response.status_code == 200:
        measurement_data = response.json()
        return measurement_data
    else:
        print(f"Failed to fetch measurement data. Status code: {response.status_code}")
        return None

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
    measurements = fetch_measurements()
    for measurement in measurements:
        print("Measurement:")
        print(f"  Input URL: {measurement['input']}")
        print(f"  Measurement UID: {measurement['measurement_uid']}")
        print(f"  Measurement Start Time: {measurement['measurement_start_time']}")
        print(f"  Probe ASN: {measurement['probe_asn']}")
        print(f"  Probe CC: {measurement['probe_cc']}")
        print(f"  Measurement URL: {measurement['measurement_url']}")
        
        measurement_data = fetch_measurement_data(measurement['measurement_url'])
        if measurement_data:
            # Process measurement data to extract certificate chains
            certificate_chains = extract_certificate_chains(measurement_data)
            print("Certificate Chains:")
            print(certificate_chains)
        else:
            print("Failed to fetch measurement data.")
        print()