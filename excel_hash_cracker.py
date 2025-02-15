import subprocess
import sys

def extract_hash(file_path):
    try:
        result = subprocess.run(
            ['python', 'C:\\JohnTheRipper\\run\\office2john.py', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.split(':')[1]
    except Exception as e:
        print(f"Hata: {str(e)}")
        sys.exit(1)

def crack_hash(hash_value):
    try:
        subprocess.run(
            ['hashcat', '-m', '9400', '-a', '3', hash_value, '?d?d?d?d?d?d', '--force'],
            check=True
        )
    except Exception as e:
        print(f"Hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python excel_hash_cracker.py <excel_dosyası>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    hash_value = extract_hash(file_path)
    crack_hash(hash_value) 