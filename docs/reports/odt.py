"""Minimal Flat-ODT (.fodt) writer: headings, paragraphs, bullets, tables, embedded figures,
header/footer with page numbers. Converted to .odt and .pdf with LibreOffice."""
import base64
import html
import re

from PIL import Image as PI

BLUE = "#2f5d8a"
LIGHT = "#dce6f2"
GREY = "#7a7a7a"


def _inline(text):
    """Escape XML and turn **bold**, *italic* and `code` into spans."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r'<text:span text:style-name="Tb">\1</text:span>', t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r'<text:span text:style-name="Ti">\1</text:span>', t)
    t = re.sub(r"`(.+?)`", r'<text:span text:style-name="Tc">\1</text:span>', t)
    return t


class Doc:
    def __init__(self, header_left, header_right, footer_left, footer_right, title):
        self.body = []
        self.auto = []
        self.ntab = 0
        self.nimg = 0
        self.nfig = 0
        self.ntabcap = 0
        self.h1 = 0
        self.h2 = 0
        self.meta = dict(hl=header_left, hr=header_right, fl=footer_left, fr=footer_right, title=title)

    # ------------------------------------------------------------ blocks
    def p(self, text, style="Body"):
        self.body.append(f'<text:p text:style-name="{style}">{_inline(text)}</text:p>')

    def raw(self, xml):
        self.body.append(xml)

    def h(self, text, level=1, numbered=True):
        if level == 1:
            if numbered:
                self.h1 += 1
                self.h2 = 0
                text = f"{self.h1}.  {text}"
            self.body.append(f'<text:h text:style-name="H1" text:outline-level="1">{_inline(text)}</text:h>')
        else:
            if numbered:
                self.h2 += 1
                text = f"{self.h1}.{self.h2}  {text}"
            self.body.append(f'<text:h text:style-name="H2" text:outline-level="2">{_inline(text)}</text:h>')

    def bullets(self, items):
        for it in items:
            self.body.append(f'<text:p text:style-name="Bullet">•<text:tab/>{_inline(it)}</text:p>')

    def numbered(self, items):
        for i, it in enumerate(items, 1):
            self.body.append(f'<text:p text:style-name="Bullet">{i}.<text:tab/>{_inline(it)}</text:p>')

    def note(self, text):
        self.p(text, "Note")

    def code(self, lines):
        for ln in lines:
            t = html.escape(ln, quote=False)
            t = re.sub(r"( {2,})", lambda m: f'<text:s text:c="{len(m.group(1))}"/>', t)
            self.body.append(f'<text:p text:style-name="Code">{t}</text:p>')
        self.body.append('<text:p text:style-name="Small"/>')

    def page_break(self):
        self.body.append('<text:p text:style-name="Break"/>')

    def spacer(self):
        self.body.append('<text:p text:style-name="Small"/>')

    def table(self, rows, widths_cm, caption=None, header=True):
        self.ntab += 1
        name = f"Tab{self.ntab}"
        total = sum(widths_cm)
        self.auto.append(f'<style:style style:name="{name}" style:family="table"><style:table-properties '
                         f'style:width="{total}cm" table:align="center" fo:margin-bottom="0.25cm"/></style:style>')
        cols = []
        for i, w in enumerate(widths_cm):
            cs = f"{name}.C{i}"
            self.auto.append(f'<style:style style:name="{cs}" style:family="table-column">'
                             f'<style:table-column-properties style:column-width="{w}cm"/></style:style>')
            cols.append(f'<table:table-column table:style-name="{cs}"/>')
        if caption:
            self.ntabcap += 1
            self.body.append(f'<text:p text:style-name="Caption">Table {self.ntabcap}: {_inline(caption)}</text:p>')
        out = [f'<table:table table:name="{name}" table:style-name="{name}">', *cols]
        for r, row in enumerate(rows):
            head = header and r == 0
            if head:
                out.append("<table:table-header-rows>")
            out.append("<table:table-row>")
            for c in row:
                out.append(f'<table:table-cell table:style-name="{"TH" if head else "TD"}" office:value-type="string">'
                           f'<text:p text:style-name="{"TableHead" if head else "TableCell"}">{_inline(str(c))}'
                           f"</text:p></table:table-cell>")
            out.append("</table:table-row>")
            if head:
                out.append("</table:table-header-rows>")
        out.append("</table:table>")
        self.body.append("".join(out))
        self.body.append('<text:p text:style-name="Small"/>')

    def figure(self, path, caption, width_cm=16.0):
        self.nimg += 1
        self.nfig += 1
        w, h = PI.open(path).size
        hcm = width_cm * h / w
        if hcm > 19.5:
            hcm = 19.5
            width_cm = hcm * w / h
        data = base64.b64encode(open(path, "rb").read()).decode()
        self.body.append(
            f'<text:p text:style-name="Figure"><draw:frame draw:style-name="fr1" draw:name="img{self.nimg}" '
            f'text:anchor-type="as-char" svg:width="{width_cm:.2f}cm" svg:height="{hcm:.2f}cm" draw:z-index="0">'
            f'<draw:image><office:binary-data>{data}</office:binary-data></draw:image></draw:frame></text:p>')
        self.body.append(f'<text:p text:style-name="Caption">Figure {self.nfig}: {_inline(caption)}</text:p>')
        return self.nfig

    # ------------------------------------------------------------ output
    def save(self, path):
        m = self.meta
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
 xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
 xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
 office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.text">
<office:meta><dc:title>{html.escape(m["title"])}</dc:title></office:meta>
<office:font-face-decls>
 <style:font-face style:name="Liberation Sans" svg:font-family="'Liberation Sans'" style:font-family-generic="swiss"/>
 <style:font-face style:name="Liberation Mono" svg:font-family="'Liberation Mono'" style:font-family-generic="modern"/>
</office:font-face-decls>
<office:styles>
 <style:default-style style:family="paragraph">
  <style:paragraph-properties fo:hyphenation-ladder-count="no-limit"/>
  <style:text-properties style:font-name="Liberation Sans" fo:font-size="10.5pt" fo:language="en" fo:country="IN"/>
 </style:default-style>
 <style:style style:name="Standard" style:family="paragraph"/>
 <style:style style:name="Body" style:family="paragraph">
  <style:paragraph-properties fo:text-align="justify" fo:margin-bottom="0.2cm" fo:line-height="128%"/>
 </style:style>
 <style:style style:name="Small" style:family="paragraph"><style:text-properties fo:font-size="4pt"/></style:style>
 <style:style style:name="H1" style:family="paragraph" style:default-outline-level="1">
  <style:paragraph-properties fo:margin-top="0.45cm" fo:margin-bottom="0.22cm" fo:keep-with-next="always"/>
  <style:text-properties fo:font-size="14pt" fo:font-weight="bold" fo:color="{BLUE}"/>
 </style:style>
 <style:style style:name="H2" style:family="paragraph" style:default-outline-level="2">
  <style:paragraph-properties fo:margin-top="0.3cm" fo:margin-bottom="0.12cm" fo:keep-with-next="always"/>
  <style:text-properties fo:font-size="11.5pt" fo:font-weight="bold" fo:color="{BLUE}"/>
 </style:style>
 <style:style style:name="Bullet" style:family="paragraph">
  <style:paragraph-properties fo:text-align="justify" fo:margin-left="0.7cm" fo:text-indent="-0.45cm"
     fo:margin-bottom="0.1cm" fo:line-height="125%">
   <style:tab-stops><style:tab-stop style:position="0cm"/></style:tab-stops>
  </style:paragraph-properties>
 </style:style>
 <style:style style:name="Note" style:family="paragraph">
  <style:paragraph-properties fo:margin-bottom="0.22cm" fo:padding="0.15cm" fo:background-color="#fff7ed"
     fo:border-left="1.5pt solid #e07b39" fo:line-height="120%"/>
  <style:text-properties fo:font-size="9.5pt" fo:font-style="italic"/>
 </style:style>
 <style:style style:name="Code" style:family="paragraph">
  <style:paragraph-properties fo:background-color="#f3f4f6" fo:margin-left="0.3cm"/>
  <style:text-properties style:font-name="Liberation Mono" fo:font-size="8pt"/>
 </style:style>
 <style:style style:name="Figure" style:family="paragraph">
  <style:paragraph-properties fo:text-align="center" fo:margin-top="0.15cm" fo:keep-with-next="always"/>
 </style:style>
 <style:style style:name="Caption" style:family="paragraph">
  <style:paragraph-properties fo:text-align="center" fo:margin-bottom="0.3cm" fo:margin-top="0.08cm" fo:keep-with-next="auto"/>
  <style:text-properties fo:font-size="9pt" fo:font-style="italic" fo:color="#374151"/>
 </style:style>
 <style:style style:name="TableHead" style:family="paragraph">
  <style:text-properties fo:font-size="8.8pt" fo:font-weight="bold"/>
 </style:style>
 <style:style style:name="TableCell" style:family="paragraph">
  <style:paragraph-properties fo:line-height="115%"/>
  <style:text-properties fo:font-size="8.8pt"/>
 </style:style>
 <style:style style:name="Title" style:family="paragraph">
  <style:paragraph-properties fo:text-align="center" fo:margin-bottom="0.25cm"/>
  <style:text-properties fo:font-size="20pt" fo:font-weight="bold" fo:color="{BLUE}"/>
 </style:style>
 <style:style style:name="Center" style:family="paragraph">
  <style:paragraph-properties fo:text-align="center" fo:margin-bottom="0.15cm"/>
 </style:style>
 <style:style style:name="Header" style:family="paragraph">
  <style:paragraph-properties>
   <style:tab-stops><style:tab-stop style:position="17cm" style:type="right"/></style:tab-stops>
  </style:paragraph-properties>
  <style:text-properties fo:font-size="7.5pt" fo:color="{GREY}"/>
 </style:style>
 <style:style style:name="Footer" style:family="paragraph" style:parent-style-name="Header"/>
 <style:style style:name="Break" style:family="paragraph">
  <style:paragraph-properties fo:break-before="page"/><style:text-properties fo:font-size="2pt"/>
 </style:style>
</office:styles>
<office:automatic-styles>
 <style:page-layout style:name="pm1">
  <style:page-layout-properties fo:page-width="21cm" fo:page-height="29.7cm" fo:margin-top="1.2cm"
     fo:margin-bottom="1.1cm" fo:margin-left="2cm" fo:margin-right="2cm"/>
  <style:header-style><style:header-footer-properties fo:min-height="0.6cm" fo:margin-bottom="0.35cm"/></style:header-style>
  <style:footer-style><style:header-footer-properties fo:min-height="0.6cm" fo:margin-top="0.35cm"/></style:footer-style>
 </style:page-layout>
 <style:style style:name="Tb" style:family="text"><style:text-properties fo:font-weight="bold"/></style:style>
 <style:style style:name="Ti" style:family="text"><style:text-properties fo:font-style="italic"/></style:style>
 <style:style style:name="Tc" style:family="text"><style:text-properties style:font-name="Liberation Mono" fo:font-size="9pt"/></style:style>
 <style:style style:name="TH" style:family="table-cell"><style:table-cell-properties fo:background-color="{LIGHT}"
   fo:padding="0.07cm" fo:border="0.5pt solid #9aa5b1"/></style:style>
 <style:style style:name="TD" style:family="table-cell"><style:table-cell-properties
   fo:padding="0.07cm" fo:border="0.5pt solid #9aa5b1"/></style:style>
 <style:style style:name="fr1" style:family="graphic"><style:graphic-properties style:vertical-pos="top"
   style:vertical-rel="baseline" fo:border="none"/></style:style>
 {"".join(self.auto)}
</office:automatic-styles>
<office:master-styles>
 <style:master-page style:name="Standard" style:page-layout-name="pm1">
  <style:header><text:p text:style-name="Header">{html.escape(m["hl"])}<text:tab/>{html.escape(m["hr"])}</text:p></style:header>
  <style:footer><text:p text:style-name="Footer">{html.escape(m["fl"])}<text:tab/>{html.escape(m["fr"])}  |  Page <text:page-number text:select-page="current">1</text:page-number></text:p></style:footer>
 </style:master-page>
</office:master-styles>
<office:body><office:text>
{"".join(self.body)}
</office:text></office:body>
</office:document>
'''
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
