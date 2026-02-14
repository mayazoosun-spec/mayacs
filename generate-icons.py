#!/usr/bin/env python3
"""
图标生成脚本 - 生成 PWA 所需的各种尺寸 PNG 图标

使用方法：
    pip install Pillow cairosvg
    python generate-icons.py

或者使用在线工具：
    1. 访问 https://realfavicongenerator.net/
    2. 上传 icons/icon.svg
    3. 下载生成的图标包并解压到 icons 目录
"""

import os

# 需要生成的图标尺寸
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def generate_with_pillow():
    """使用 Pillow + cairosvg 生成图标"""
    try:
        from PIL import Image
        import cairosvg
        import io

        svg_path = 'icons/icon.svg'

        for size in SIZES:
            # 将 SVG 转换为 PNG
            png_data = cairosvg.svg2png(
                url=svg_path,
                output_width=size,
                output_height=size
            )

            # 保存 PNG
            output_path = f'icons/icon-{size}x{size}.png'
            with open(output_path, 'wb') as f:
                f.write(png_data)

            print(f'生成: {output_path}')

        print('\n所有图标生成完成!')
        return True

    except ImportError as e:
        print(f'缺少依赖: {e}')
        print('请运行: pip install Pillow cairosvg')
        return False

def generate_with_canvas_html():
    """生成一个 HTML 文件，使用 Canvas 在浏览器中生成图标"""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>图标生成器</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: white; }
        .icon-container { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px; }
        .icon-item { text-align: center; }
        canvas { border: 1px solid #333; }
        a { color: #e74c3c; }
        button { background: #e74c3c; color: white; border: none; padding: 10px 20px;
                 border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #c0392b; }
    </style>
</head>
<body>
    <h1>🍅 番茄时钟图标生成器</h1>
    <p>点击下面的按钮下载各种尺寸的图标，然后放入 icons 文件夹中。</p>
    <div id="icons" class="icon-container"></div>

    <script>
        const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
        const container = document.getElementById('icons');

        function drawIcon(ctx, size) {
            const scale = size / 512;

            // Background
            ctx.fillStyle = '#1a1a2e';
            ctx.beginPath();
            ctx.roundRect(0, 0, size, size, 100 * scale);
            ctx.fill();

            // Tomato body
            const gradient = ctx.createLinearGradient(0, 0, size, size);
            gradient.addColorStop(0, '#ff6b6b');
            gradient.addColorStop(1, '#e74c3c');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.ellipse(256 * scale, 300 * scale, 160 * scale, 150 * scale, 0, 0, Math.PI * 2);
            ctx.fill();

            // Highlight
            ctx.fillStyle = 'rgba(255,255,255,0.2)';
            ctx.beginPath();
            ctx.ellipse(200 * scale, 260 * scale, 40 * scale, 30 * scale, 0, 0, Math.PI * 2);
            ctx.fill();

            // Stem
            ctx.fillStyle = '#5d4e37';
            ctx.beginPath();
            ctx.roundRect(246 * scale, 140 * scale, 20 * scale, 40 * scale, 5 * scale);
            ctx.fill();

            // Leaves
            const leafGrad = ctx.createLinearGradient(0, 0, size, size);
            leafGrad.addColorStop(0, '#27ae60');
            leafGrad.addColorStop(1, '#1e8449');
            ctx.fillStyle = leafGrad;
            ctx.beginPath();
            ctx.moveTo(256 * scale, 160 * scale);
            ctx.quadraticCurveTo(200 * scale, 140 * scale, 180 * scale, 100 * scale);
            ctx.quadraticCurveTo(220 * scale, 120 * scale, 256 * scale, 130 * scale);
            ctx.quadraticCurveTo(292 * scale, 120 * scale, 332 * scale, 100 * scale);
            ctx.quadraticCurveTo(312 * scale, 140 * scale, 256 * scale, 160 * scale);
            ctx.fill();

            // Timer circle
            ctx.strokeStyle = 'rgba(255,255,255,0.3)';
            ctx.lineWidth = 8 * scale;
            ctx.beginPath();
            ctx.arc(256 * scale, 300 * scale, 80 * scale, 0, Math.PI * 2);
            ctx.stroke();

            // Timer arc
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 8 * scale;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.arc(256 * scale, 300 * scale, 80 * scale, -Math.PI/2, Math.PI);
            ctx.stroke();

            // Hour hand
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 6 * scale;
            ctx.beginPath();
            ctx.moveTo(256 * scale, 300 * scale);
            ctx.lineTo(256 * scale, 250 * scale);
            ctx.stroke();

            // Minute hand
            ctx.lineWidth = 4 * scale;
            ctx.beginPath();
            ctx.moveTo(256 * scale, 300 * scale);
            ctx.lineTo(290 * scale, 320 * scale);
            ctx.stroke();

            // Center dot
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(256 * scale, 300 * scale, 8 * scale, 0, Math.PI * 2);
            ctx.fill();
        }

        sizes.forEach(size => {
            const div = document.createElement('div');
            div.className = 'icon-item';

            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');

            drawIcon(ctx, size);

            const link = document.createElement('a');
            link.href = canvas.toDataURL('image/png');
            link.download = `icon-${size}x${size}.png`;

            const btn = document.createElement('button');
            btn.textContent = `下载 ${size}x${size}`;
            link.appendChild(btn);

            div.appendChild(canvas);
            div.appendChild(document.createElement('br'));
            div.appendChild(link);

            container.appendChild(div);
        });
    </script>
</body>
</html>'''

    with open('generate-icons.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print('已生成 generate-icons.html')
    print('请在浏览器中打开此文件，然后下载各尺寸的图标')

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')

    print('番茄时钟 PWA 图标生成器')
    print('=' * 40)

    if not generate_with_pillow():
        print('\n尝试生成浏览器端图标生成器...')
        generate_with_canvas_html()

if __name__ == '__main__':
    main()
