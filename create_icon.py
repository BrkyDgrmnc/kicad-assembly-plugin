"""
KiCad Eklenti İkonu Üretici (64x64 PNG)
"""

import zlib
import struct

def create_png_icon(filename="icon.png", width=64, height=64):
    # 64x64 RGBA Image with a sleek dark blue/teal chip icon
    raw_data = bytearray()
    
    for y in range(height):
        raw_data.append(0) # Filter type 0 (None)
        for x in range(width):
            # Border
            if x == 0 or x == width-1 or y == 0 or y == height-1:
                r, g, b, a = 30, 41, 59, 255 # Slate 800
            # Chip body (center rectangle 12..51)
            elif 12 <= x <= 51 and 12 <= y <= 51:
                if 14 <= x <= 49 and 14 <= y <= 49:
                    r, g, b, a = 15, 23, 42, 255 # Deep Dark Blue
                else:
                    r, g, b, a = 51, 65, 85, 255 # Chip border
            # IC Pins (left/right/top/bottom)
            elif (y in (8, 9, 10, 11, 52, 53, 54, 55) and x in (18, 26, 34, 42, 45)) or \
                 (x in (8, 9, 10, 11, 52, 53, 54, 55) and y in (18, 26, 34, 42, 45)):
                r, g, b, a = 245, 158, 11, 255 # Gold Pin
            # Background
            else:
                r, g, b, a = 241, 245, 249, 255 # Soft Light Slate

            raw_data.extend([r, g, b, a])

    def make_chunk(chunk_type, data):
        length = len(data)
        crc = zlib.crc32(chunk_type + data) & 0xffffffff
        return struct.pack('>I', length) + chunk_type + data + struct.pack('>I', crc)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr_chunk = make_chunk(b'IHDR', ihdr)
    
    idat_data = zlib.compress(raw_data)
    idat_chunk = make_chunk(b'IDAT', idat_data)
    
    iend_chunk = make_chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(header + ihdr_chunk + idat_chunk + iend_chunk)

if __name__ == "__main__":
    create_png_icon()
    print("icon.png successfully created!")
