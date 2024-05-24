import heapq
from collections import defaultdict
from pathlib import Path
import sys

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_dict(data):
    frequency = defaultdict(int)
    for char in data:
        frequency[char] += 1
    return frequency

def build_huffman_tree(frequency):
    priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)

    return priority_queue[0]

def build_codes(root):
    codes = {}

    def _build_codes_helper(node, current_code):
        if node:
            if node.char:
                codes[node.char] = current_code
            _build_codes_helper(node.left, current_code + "0")
            _build_codes_helper(node.right, current_code + "1")

    _build_codes_helper(root, "")
    return codes

def encode_data(data, codes):
    encoded_data = "".join(codes[char] for char in data)
    padding = 8 - len(encoded_data) % 8
    encoded_data += "0" * padding
    padded_info = f"{padding:08b}"
    return padded_info + encoded_data

def decode_data(encoded_data, root):
    padding = int(encoded_data[:8], 2)
    encoded_data = encoded_data[8:-padding]

    decoded_data = []
    current_node = root
    for bit in encoded_data:
        current_node = current_node.left if bit == "0" else current_node.right
        if current_node.char:
            decoded_data.append(current_node.char)
            current_node = root

    return "".join(decoded_data)

def huffman_compress(input_file, output_file):
    try:
        with open(input_file, "r") as f:
            data = f.read()
    except Exception as e:
        print(f"Błąd podczas odczytu pliku wejściowego: {e}")
        sys.exit(1)

    frequency = build_frequency_dict(data)
    huffman_tree = build_huffman_tree(frequency)
    codes = build_codes(huffman_tree)
    encoded_data = encode_data(data, codes)

    try:
        with open(output_file, "wb") as f:
            f.write(len(frequency).to_bytes(2, 'big'))
            for char, freq in frequency.items():
                f.write(char.encode())
                f.write(freq.to_bytes(4, 'big'))
            encoded_bytes = bytearray(int(encoded_data[i:i+8], 2) for i in range(0, len(encoded_data), 8))
            f.write(encoded_bytes)
    except Exception as e:
        print(f"Błąd podczas zapisu pliku wyjściowego: {e}")
        sys.exit(1)

def huffman_decompress(input_file, output_file):
    try:
        with open(input_file, "rb") as f:
            frequency_length = int.from_bytes(f.read(2), 'big')
            frequency = {f.read(1).decode(): int.from_bytes(f.read(4), 'big') for _ in range(frequency_length)}
            huffman_tree = build_huffman_tree(frequency)
            encoded_data = "".join(f"{int.from_bytes(byte, 'big'):08b}" for byte in iter(lambda: f.read(1), b''))
    except Exception as e:
        print(f"Błąd podczas odczytu pliku wejściowego: {e}")
        sys.exit(1)

    decoded_data = decode_data(encoded_data, huffman_tree)

    try:
        with open(output_file, "w") as f:
            f.write(decoded_data)
    except Exception as e:
        print(f"Błąd podczas zapisu pliku wyjściowego: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Użycie: python huffman.py compress|decompress <plik_wejściowy> <plik_wyjściowy>")
        sys.exit(1)

    command = sys.argv[1]
    input_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    if command == "compress":
        huffman_compress(input_file, output_file)
    elif command == "decompress":
        huffman_decompress(input_file, output_file)
    else:
        print("Niepoprawna komenda. Użyj 'compress' lub 'decompress'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
