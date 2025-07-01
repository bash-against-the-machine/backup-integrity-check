#! /usr/bin/python3

import argparse
import os
import hashlib
from typing import Dict

try:
    from termcolor import colored
    termcolor_installed = True
except ImportError:
    termcolor_installed = False
    def colored(text, color):
        return text  # fallback if termcolor is not installed


def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_hashes(hash_file: str) -> Dict[str, str]:
    hashes = {}
    with open(hash_file, 'r') as f:
        for line in f:
            if ':::' in line:
                rel_path, hashval = line.strip().split(':::', 1)
                hashes[rel_path] = hashval
    return hashes


def verify_hashes(directory: str, hash_file: str):
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        exit(1)
    if not os.path.isfile(hash_file):
        print(f"Error: {hash_file} does not exist.")
        exit(1)

    hashes = load_hashes(hash_file)
    print(f"[DEBUG] Loaded hash keys: {list(hashes.keys())}")
    verified_count = 0
    failed_count = 0
    results = []

    # Find the longest file name for alignment
    max_file_len = max((len(file) for root, _, files in os.walk(directory) for file in files), default=0)
    status_col = max_file_len + 8  # 8 is a buffer for spacing and dashes

    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, directory)
            print(f"[DEBUG] Verifying: rel_path='{rel_path}' for file '{filepath}'")
            hash_value = calculate_sha256(filepath)
            expected_hash = hashes.get(rel_path)
            if expected_hash == hash_value:
                status = colored('verified', 'green')
                verified_count += 1
            else:
                status = colored('failed verification', 'red')
                failed_count += 1
            dash_count = status_col - len(rel_path)
            dashes = '-' * dash_count
            result_line = f"{rel_path} {dashes} {status}"
            print(result_line)
            results.append(result_line)

    total_files = verified_count + failed_count

    summary_title = "Summary"
    box_width = len(summary_title) + 2
    top_bottom_border = '-' * box_width
    summary_header = f"|{summary_title}|"

    # Console Summary
    print(f"\n{top_bottom_border}")
    print(summary_header)
    print(top_bottom_border)
    print(f"Total files: {total_files}")
    print(f"Verified: {verified_count}")
    failed_line = f"Failed Verification: {failed_count}"
    if failed_count > 0:
        print(colored(failed_line, 'red'))
    else:
        print(failed_line)


    # File Summary
    with open('backup_verification_summary.txt', 'w') as out:
        for line in results:
            out.write(line + '\n')
        out.write(f"\n{top_bottom_border}\n")
        out.write(f"{summary_header}\n")
        out.write(f"{top_bottom_border}\n")
        out.write(f"Total files: {total_files}\n")
        out.write(f"Verified: {verified_count}\n")
        out.write(f"Failed Verification: {failed_count}\n")


def main():
    parser = argparse.ArgumentParser(description='Backup Integrity Check: Generate or verify SHA256 hashes for files in a directory.')
    parser.add_argument('-b', '--backup', help='Directory to enumerate and hash files from')
    parser.add_argument('-v', '--verify', nargs=2, metavar=('DIRECTORY', 'HASHFILE'), help='Verify hashes in DIRECTORY using HASHFILE')
    args = parser.parse_args()

    if not termcolor_installed:
        print("[Warning] For colored output, install 'termcolor' via 'pip install termcolor'.")

    if args.backup:
        directory = args.backup
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a valid directory.")
            exit(1)
        output_file = 'backup_hashes.txt'
        with open(output_file, 'w') as out:
            for root, _, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, directory)
                    print(f"[DEBUG] Writing: rel_path='{rel_path}' for file '{filepath}'")
                    try:
                        hash_value = calculate_sha256(filepath)
                        out.write(f"{rel_path}:::{hash_value}\n")
                    except Exception as e:
                        print(f"Failed to hash {filepath}: {e}")
    elif args.verify:
        verify_hashes(args.verify[0], args.verify[1])
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

