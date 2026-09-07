import math

def generate_ashoka_chakra_svg(size=120, color='#0A369D'):
    cx, cy = size / 2, size / 2
    r_outer = size * 0.46
    r_inner = size * 0.41
    r_hub = size * 0.11
    r_hub_inner = size * 0.045
    
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">']
    # Outer ring
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="{color}" stroke-width="{size*0.035}"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="{color}" stroke-width="{size*0.015}"/>')
    
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
        
        svg.append(f'<polygon points="{bx1:.2f},{by1:.2f} {tx:.2f},{ty:.2f} {bx2:.2f},{by2:.2f}" fill="{color}"/>')
        
        # Small circle between spokes at outer edge
        dot_rad = math.radians(deg + 7.5)
        dot_r = (r_outer + r_inner) / 2
        dx = cx + dot_r * math.cos(dot_rad)
        dy = cy + dot_r * math.sin(dot_rad)
        svg.append(f'<circle cx="{dx:.2f}" cy="{dy:.2f}" r="{size*0.014:.2f}" fill="{color}"/>')
    
    # Central Hub
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_hub}" fill="{color}"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_hub_inner}" fill="#ffffff"/>')
    svg.append('</svg>')
    return '\n'.join(svg)

svg_code = generate_ashoka_chakra_svg(120, '#0A369D')
out_svg = r'c:\Users\yashr\.gemini\antigravity\scratch\setu\api\app\static\ashoka_chakra.svg'
with open(out_svg, 'w', encoding='utf-8') as f:
    f.write(svg_code)

print('Ashoka Chakra SVG generated at:', out_svg)
