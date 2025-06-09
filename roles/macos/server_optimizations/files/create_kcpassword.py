#!/usr/bin/env python3
"""
Script to create macOS kcpassword file for auto-login
Usage: python3 create_kcpassword.py <password>
"""
import sys
import os

def create_kcpassword(password):
    """Create encoded kcpassword file for macOS auto-login"""
    # XOR key used by macOS for kcpassword encoding
    key = [125, 137, 82, 35, 210, 188, 221, 234, 163, 185, 31]
    
    # Pad password to multiple of 12 bytes, truncate if longer than 12
    if len(password) > 12:
        password_padded = password[:12]
    else:
        password_padded = password + '\x00' * (12 - len(password))
    
    # Encode password using XOR with key
    encoded = bytearray()
    for i, char in enumerate(password_padded):
        encoded.append(ord(char) ^ key[i % len(key)])
    
    # Write to /etc/kcpassword
    try:
        with open('/etc/kcpassword', 'wb') as f:
            f.write(encoded)
        os.chmod('/etc/kcpassword', 0o600)
        print("kcpassword file created successfully")
        return True
    except Exception as e:
        print(f"Error creating kcpassword file: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 create_kcpassword.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    success = create_kcpassword(password)
    sys.exit(0 if success else 1)