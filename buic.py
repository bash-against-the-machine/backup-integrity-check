#! /usr/bin/python3

import argparse
import os
import hashlib
from typing import Dict
import datetime

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
    now = datetime.datetime.now()
    abs_dir = os.path.abspath(directory)
    dir_part = abs_dir.lstrip(os.sep).replace(os.sep, '_')
    summary_file = f"{dir_part}_hashverified_{now:%m_%d_%Y}.txt"
    with open(summary_file, 'w') as out:
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
        now = datetime.datetime.now()
        abs_dir = os.path.abspath(directory)
        dir_part = abs_dir.lstrip(os.sep).replace(os.sep, '_')
        output_file = f"{dir_part}_hashes_{now:%m_%d_%Y}.txt"
        # Collect all files first for progress bar
        all_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                all_files.append((filepath, rel_path))
        total_files = len(all_files)
        with open(output_file, 'w') as out:
            for idx, (filepath, rel_path) in enumerate(all_files, 1):
                # Clear the line before printing the new file name
                print('\r' + ' ' * 70 + '\r', end='')
                # Limit the display to 80 characters total
                display_text = f"Hashing: {rel_path}"
                if len(display_text) > 70:
                    # Truncate the path and add ellipsis
                    max_path_len = 70 - len("Hashing: ...")
                    truncated_path = rel_path[:max_path_len] + "..."
                    display_text = f"Hashing: {truncated_path}"
                print(display_text, end='\r')
                try:
                    hash_value = calculate_sha256(filepath)
                    out.write(f"{rel_path}:::{hash_value}\n")
                except Exception as e:
                    print(f"Failed to hash {filepath}: {e}")
                # Progress bar
                percent = int((idx / total_files) * 100)
                bar_len = 60
                filled_len = int(bar_len * idx // total_files)
                bar = '#' * filled_len + '-' * (bar_len - filled_len)
                print(f"\n[{bar}] {percent}% ({idx}/{total_files})", end='\033[F' if idx < total_files else '\n')
    elif args.verify:
        verify_hashes(args.verify[0], args.verify[1])
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

