import struct, zlib, math

def generate_chakra_elements(cx, cy, r):
    # Generates SVG elements for Ashoka Chakra centered at (cx, cy) with radius r
    color = '#0A369D'
    r_outer = r * 0.94
    r_inner = r * 0.83
    r_hub = r * 0.22
    r_hub_inner = r * 0.09
    
    elems = []
    # Outer circle rings
    elems.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_outer:.1f}" fill="#FFFFFF" stroke="{color}" stroke-width="{r*0.07:.1f}"/>')
    elems.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_inner:.1f}" fill="none" stroke="{color}" stroke-width="{r*0.03:.1f}"/>')
    
    # 24 Spokes
    for i in range(24):
        deg = i * 15
        rad = math.radians(deg)
        rad_left = math.radians(deg - 2.2)
        rad_right = math.radians(deg + 2.2)
        
        tx = cx + r_inner * math.cos(rad)
        ty = cy + r_inner * math.sin(rad)
        
        bx1 = cx + r_hub * math.cos(rad_left)
        by1 = cy + r_hub * math.sin(rad_left)
        bx2 = cx + r_hub * math.cos(rad_right)
        by2 = cy + r_hub * math.sin(rad_right)
        
        elems.append(f'<polygon points="{bx1:.2f},{by1:.2f} {tx:.2f},{ty:.2f} {bx2:.2f},{by2:.2f}" fill="{color}"/>')
        
        # Dots between spokes
        dot_rad = math.radians(deg + 7.5)
        dot_r = (r_outer + r_inner) / 2
        dx = cx + dot_r * math.cos(dot_rad)
        dy = cy + dot_r * math.sin(dot_rad)
        elems.append(f'<circle cx="{dx:.2f}" cy="{dy:.2f}" r="{r*0.03:.2f}" fill="{color}"/>')
        
    # Central Hub
    elems.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_hub:.1f}" fill="{color}"/>')
    elems.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_hub_inner:.1f}" fill="#FFFFFF"/>')
    return '\n    '.join(elems)

def generate_monuments():
    with open('api/app/static/monuments_white_hd.png', 'rb') as f:
        data = f.read()

    chunks = []
    pos = 8
    while pos < len(data):
        length, chunk_type = struct.unpack('>I4s', data[pos:pos+8])
        chunk_data = data[pos+8:pos+8+length]
        chunks.append((chunk_type, chunk_data))
        pos += 12 + length

    idat = b''.join(c[1] for c in chunks if c[0] == b'IDAT')
    decomp = bytearray(zlib.decompress(idat))
    w, h = 1482, 280
    stride = 1 + w * 4

    # Build pure vector path runs
    path_cmds = []
    for y in range(h):
        row = y * stride
        in_run = False
        start_x = 0
        for x in range(w):
            a = decomp[row + 1 + x * 4 + 3]
            if a > 120 and not in_run:
                in_run = True
                start_x = x
            elif a <= 120 and in_run:
                in_run = False
                path_cmds.append(f'M{start_x} {y}h{x - start_x}v1h{start_x - x}z')
        if in_run:
            path_cmds.append(f'M{start_x} {y}h{w - start_x}v1h{start_x - w}z')

    # Add continuous ground baseline spanning 0 to w
    path_cmds.append(f'M0 277h{w}v3h-{w}z')
    d = ''.join(path_cmds)
    print(f'Total vector path runs: {len(path_cmds)}, path length: {len(d)}')

    chakra_svg = generate_chakra_elements(741, 46, 32)

    # 1. Main stretch-to-fit SVG (preserveAspectRatio="none")
    svg_stretch = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="none">
  <defs>
    <linearGradient id="monumentsTiranga" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF671F"/>
      <stop offset="30%" stop-color="#FF8A38"/>
      <stop offset="46%" stop-color="#FFFFFF"/>
      <stop offset="54%" stop-color="#FFFFFF"/>
      <stop offset="70%" stop-color="#22C55E"/>
      <stop offset="100%" stop-color="#16A34A"/>
    </linearGradient>
    <filter id="chakraGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="3" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>
  <!-- Silhouette Path Filled with Saffron -> White -> Green Gradient -->
  <path fill="url(#monumentsTiranga)" d="{d}"/>
  <!-- Centered Ashoka Chakra in the White Middle Band above India Gate -->
  <g filter="url(#chakraGlow)">
    {chakra_svg}
  </g>
</svg>'''

    with open('api/app/static/monuments_skyline.svg', 'w', encoding='utf-8') as f:
        f.write(svg_stretch)
    print('Generated api/app/static/monuments_skyline.svg')

    # 2. Responsive aspect-ratio preserving version (xMidYMax meet)
    svg_meet = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMax meet">
  <defs>
    <linearGradient id="monumentsTirangaMeet" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF671F"/>
      <stop offset="30%" stop-color="#FF8A38"/>
      <stop offset="46%" stop-color="#FFFFFF"/>
      <stop offset="54%" stop-color="#FFFFFF"/>
      <stop offset="70%" stop-color="#22C55E"/>
      <stop offset="100%" stop-color="#16A34A"/>
    </linearGradient>
    <filter id="chakraGlowMeet" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="3" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>
  <path fill="url(#monumentsTirangaMeet)" d="{d}"/>
  <g filter="url(#chakraGlowMeet)">
    {chakra_svg}
  </g>
</svg>'''

    with open('api/app/static/monuments_responsive.svg', 'w', encoding='utf-8') as f:
        f.write(svg_meet)
    print('Generated api/app/static/monuments_responsive.svg')

    # 3. High-def PNG companion with Saffron -> White -> Green gradient
    for y in range(h):
        row = y * stride
        for x in range(w):
            px = row + 1 + x * 4
            a = decomp[px + 3]
            if a > 0:
                t = x / (w - 1)
                if t < 0.46:
                    u = t / 0.46
                    u = u * u * (3 - 2 * u)
                    r = int(255 * (1 - u) + 255 * u)
                    g = int(103 * (1 - u) + 255 * u)
                    b = int(31 * (1 - u) + 255 * u)
                elif t <= 0.54:
                    r, g, b = 255, 255, 255
                else:
                    u = (t - 0.54) / 0.46
                    u = u * u * (3 - 2 * u)
                    r = int(255 * (1 - u) + 22 * u)
                    g = int(255 * (1 - u) + 163 * u)
                    b = int(255 * (1 - u) + 74 * u)
                decomp[px] = r
                decomp[px + 1] = g
                decomp[px + 2] = b

    def make_chunk(chunk_type, chunk_data):
        return struct.pack('>I4s', len(chunk_data), chunk_type) + chunk_data + struct.pack('>I', zlib.crc32(chunk_type + chunk_data) & 0xffffffff)

    new_idat = zlib.compress(bytes(decomp), 9)
    out_png = bytearray(b'\x89PNG\r\n\x1a\n')
    out_png += make_chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    out_png += make_chunk(b'IDAT', new_idat)
    out_png += make_chunk(b'IEND', b'')

    with open('api/app/static/monuments_saffron_white_green_hd.png', 'wb') as f:
        f.write(out_png)
    print('Generated api/app/static/monuments_saffron_white_green_hd.png')

if __name__ == '__main__':
    generate_monuments()
