#!/usr/bin/env python3
"""
Converte README.md em PDF estilizado para entrega do relatorio CardioIA.
Sem parametros — sempre processa o README.md da raiz do projeto.
"""

import importlib
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from weasyprint import HTML

pygments_spec = importlib.util.find_spec("pygments.formatters.html")
HtmlFormatter = None
if pygments_spec:
    HtmlFormatter = importlib.import_module("pygments.formatters.html").HtmlFormatter

PROJECT_ROOT = Path(__file__).resolve().parent
MD_FILE = PROJECT_ROOT / "README.md"
OUTPUT_PDF = PROJECT_ROOT / "CardioIA-Relatorio.pdf"
ACCENT_COLOR = "#3498db"


def _normalize_hex_color(color: str) -> str | None:
    color = color.strip()
    if not color:
        return None
    if color.startswith('#'):
        hex_value = color[1:]
    else:
        hex_value = color
    if len(hex_value) in {3, 6} and all(c in '0123456789abcdefABCDEF' for c in hex_value):
        if len(hex_value) == 3:
            hex_value = ''.join(ch * 2 for ch in hex_value)
        return f"#{hex_value.lower()}"
    return None


def _lighten_hex_color(color: str, factor: float) -> str:
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    lighten = tuple(int(((255 - c) * factor) + c) for c in rgb)
    return f"#{lighten[0]:02x}{lighten[1]:02x}{lighten[2]:02x}"


def _resolve_color(color_input: str) -> tuple[str, str]:
    hex_color = _normalize_hex_color(color_input)
    if hex_color is not None:
        return hex_color, _lighten_hex_color(hex_color, 0.85)
    stripped = color_input.replace('-', '').replace('_', '')
    if stripped.isalpha():
        return color_input, '#f1f5f9'
    print(f"Error: Invalid color '{color_input}'. Use a hex value (e.g. #663399) or CSS color name.")
    sys.exit(1)


def convert():
    if not MD_FILE.exists():
        print(f"Erro: {MD_FILE} nao encontrado.")
        sys.exit(1)

    with open(MD_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Preprocess: numbered code refs → python blocks
    md_content = re.sub(
        r'^```(\d+:\d+:[^\n]+)$',
        r'```python',
        md_content,
        flags=re.MULTILINE,
    )

    # Preprocess: --- before ## PARTE headers → page break marker
    # Only insert page breaks before major section headers
    md_content = md_content.replace(
        '\n---\n\n## PARTE 1',
        '\n<div class="page-break"></div>\n\n## PARTE 1',
    )
    md_content = md_content.replace(
        '\n---\n\n## PARTE 2',
        '\n<div class="page-break"></div>\n\n## PARTE 2',
    )
    md_content = md_content.replace(
        '\n---\n\n## Historico',
        '\n<div class="page-break"></div>\n\n## Historico',
    )
    md_content = md_content.replace(
        '\n---\n\n## Licenca',
        '\n<div class="page-break"></div>\n\n## Licenca',
    )

    accent_color, accent_tint = _resolve_color(ACCENT_COLOR)

    # Markdown → HTML with syntax highlighting
    formatter_css = ""
    codehilite_config = {
        'guess_lang': True,
        'pygments_style': 'default',
        'noclasses': HtmlFormatter is None,
    }
    if HtmlFormatter is not None:
        formatter_css = HtmlFormatter(style='default').get_style_defs('.codehilite')

    html_content = markdown.markdown(
        md_content,
        extensions=[
            'extra',
            'fenced_code',
            'tables',
            CodeHiliteExtension(**codehilite_config),
        ],
    )

    styled_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="utf-8">
        <style>
            {formatter_css}

            @page {{
                size: A4;
                margin: 2cm 2cm 2cm 2cm;
                @bottom-center {{
                    content: counter(page);
                    font-size: 0.8em;
                    color: #888;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 11pt;
            }}

            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid {accent_color};
                padding-bottom: 10px;
                margin-top: 0;
                font-size: 2em;
                font-weight: 600;
                page-break-after: avoid;
                break-after: avoid-page;
            }}

            h2 {{
                color: #34495e;
                margin-top: 28px;
                margin-bottom: 14px;
                font-size: 1.5em;
                font-weight: 500;
                border-left: 4px solid {accent_color};
                padding-left: 14px;
                page-break-after: avoid;
                break-after: avoid-page;
            }}

            h3 {{
                color: #555;
                margin-top: 20px;
                font-size: 1.2em;
                page-break-after: avoid;
                break-after: avoid-page;
            }}

            h4 {{
                color: #666;
                margin-top: 16px;
                font-size: 1.05em;
                page-break-after: avoid;
                break-after: avoid-page;
            }}

            p {{
                margin: 10px 0;
                text-align: justify;
                orphans: 3;
                widows: 3;
            }}

            a {{
                color: {accent_color};
                word-break: break-all;
            }}

            /* Tables */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 14px 0;
                font-size: 0.9em;
                page-break-inside: avoid;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }}

            th {{
                background: {accent_color};
                color: white;
                font-weight: 600;
            }}

            tr:nth-child(even) {{
                background: #f8f9fa;
            }}

            /* Code blocks */
            pre {{
                background: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid {accent_color};
                padding: 12px 16px;
                overflow-x: auto;
                font-family: "Fira Code", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                font-size: 0.82em;
                line-height: 1.45;
                margin: 14px 0;
                white-space: pre-wrap;
                word-wrap: break-word;
                word-break: break-all;
                overflow-wrap: break-word;
                page-break-inside: avoid;
            }}

            .codehilite {{
                background: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid {accent_color};
                padding: 12px 16px;
                margin: 14px 0;
                overflow-x: auto;
                page-break-inside: avoid;
            }}

            .codehilite pre {{
                margin: 0;
                padding: 0;
                background: transparent;
                border: none;
            }}

            /* Inline code */
            code {{
                font-family: "Fira Code", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                background: {accent_tint};
                color: #c7254e;
                padding: 1px 5px;
                border-radius: 3px;
                font-size: 0.88em;
                word-break: break-all;
            }}

            pre code {{
                display: block;
                padding: 0;
                background: transparent;
                color: #2c3e50;
                font-size: inherit;
                word-break: normal;
            }}

            /* Images */
            img {{
                max-width: 100%;
                max-height: 460px;
                width: auto;
                height: auto;
                display: block;
                margin: 8px auto;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                page-break-inside: avoid;
            }}

            /* Image captions */
            blockquote {{
                border-left: 3px solid {accent_tint};
                margin: 8px 0 18px 0;
                padding: 6px 14px;
                color: #666;
                font-style: italic;
                font-size: 0.92em;
                background: #fafafa;
                page-break-inside: avoid;
            }}

            /* Lists */
            ul, ol {{
                margin: 8px 0;
                padding-left: 24px;
            }}

            li {{
                margin: 4px 0;
            }}

            /* Page break */
            .page-break {{
                page-break-before: always;
                break-before: page;
                height: 0;
                margin: 0;
                padding: 0;
                border: none;
            }}

            /* Horizontal rule */
            hr {{
                border: none;
                border-top: 1px solid #ddd;
                margin: 20px 0;
            }}

            /* Strong emphasis */
            strong {{
                color: #2c3e50;
            }}

            /* Pygments syntax highlighting */
            .highlight .c {{ color: #999988; font-style: italic; }}
            .highlight .k {{ color: #0000ff; font-weight: bold; }}
            .highlight .kn {{ color: #0000ff; font-weight: bold; }}
            .highlight .s, .highlight .s1, .highlight .s2 {{ color: #d14; }}
            .highlight .nf {{ color: #990000; font-weight: bold; }}
            .highlight .nc {{ color: #445588; font-weight: bold; }}
            .highlight .nb {{ color: #0086B3; }}
            .highlight .mi, .highlight .mf {{ color: #009999; }}
            .highlight .bp {{ color: #999999; }}
            .highlight .o {{ color: #000000; font-weight: bold; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    print(f"Convertendo {MD_FILE.name} para PDF...")
    html_doc = HTML(string=styled_html, base_url=str(PROJECT_ROOT))
    html_doc.write_pdf(OUTPUT_PDF)

    size_kb = OUTPUT_PDF.stat().st_size / 1024
    print(f"PDF gerado: {OUTPUT_PDF} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    convert()
