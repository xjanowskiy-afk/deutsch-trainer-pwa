import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont('DejaVu', 8)
        self.setFillColor(colors.HexColor('#64748b'))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 810, "Bürger GmbH / JobImpulse • Fachwortschatz Lebensmittelherstellung & Verpackung")
            self.drawRightString(555, 810, "Roman Aleksieiev (B1)")
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(40, 803, 555, 803)

        # Footer
        text = f"Страница {self._pageNumber} из {page_count}"
        self.drawRightString(555, 25, text)
        self.drawString(40, 25, "Тренажер немецкого языка • Практическая лексика для цеха упаковки")
        self.setStrokeColor(colors.HexColor('#e2e8f0'))
        self.setLineWidth(0.5)
        self.line(40, 36, 555, 36)
        
        self.restoreState()

def build_pdf(json_path, pdf_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='DejaVu-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=0,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='DejaVu',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0369a1'),
        alignment=0,
        spaceAfter=12
    )
    cat_header_style = ParagraphStyle(
        'CatHeader',
        fontName='DejaVu-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    term_style_blue = ParagraphStyle(
        'TermBlue',
        fontName='DejaVu-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1d4ed8')
    )
    term_style_red = ParagraphStyle(
        'TermRed',
        fontName='DejaVu-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#b91c1c')
    )
    term_style_green = ParagraphStyle(
        'TermGreen',
        fontName='DejaVu-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#15803d')
    )
    term_style_orange = ParagraphStyle(
        'TermOrange',
        fontName='DejaVu-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#c2410c')
    )
    term_style_dark = ParagraphStyle(
        'TermDark',
        fontName='DejaVu-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a')
    )
    body_style = ParagraphStyle(
        'BodyTextRu',
        fontName='DejaVu',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#334155')
    )
    transcription_style = ParagraphStyle(
        'TransStyle',
        fontName='DejaVu',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#64748b')
    )
    example_style = ParagraphStyle(
        'ExStyle',
        fontName='DejaVu',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0284c7')
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Профессиональный словарь: Пищевое производство и упаковка", title_style))
    story.append(Paragraph("<b>Fachwortschatz für Lebensmittelherstellung & Verpackung</b> • Bürger GmbH & Co. KG (Ditzingen) / JobImpulse Süd GmbH • Кандидат: Роман Алексеев", subtitle_style))
    
    # Legend box
    legend_text = (
        "<b>Цветовая индикация рода:</b> "
        "<font color='#1d4ed8'>■ der (мужской)</font> | "
        "<font color='#b91c1c'>■ die (женский)</font> | "
        "<font color='#15803d'>■ das (средний)</font> | "
        "<font color='#c2410c'>■ die Pl. (множественное число)</font>"
    )
    legend_style = ParagraphStyle('Legend', fontName='DejaVu', fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'))
    
    legend_table = Table([[Paragraph(legend_text, legend_style)]], colWidths=[523])
    legend_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 10))

    # Group by category
    categories = {}
    for item in data['items']:
        cat = item['category'] or "Общая лексика"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    for cat_name, cat_items in categories.items():
        story.append(Paragraph(cat_name, cat_header_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94a3b8'), spaceBefore=2, spaceAfter=6))
        
        table_data = []
        # Header row
        table_data.append([
            Paragraph("<b>№</b>", body_style),
            Paragraph("<b>Немецкий термин / Артикль / Плюрал</b>", body_style),
            Paragraph("<b>Транскрипция и русский перевод</b>", body_style),
            Paragraph("<b>Пример в цехе (A2-B1) + Перевод</b>", body_style)
        ])

        for item in cat_items:
            # Pick term style
            if item['gender'] == 'masculine':
                t_style = term_style_blue
            elif item['gender'] == 'feminine':
                t_style = term_style_red
            elif item['gender'] == 'neuter':
                t_style = term_style_green
            elif item['gender'] == 'plural':
                t_style = term_style_orange
            else:
                t_style = term_style_dark

            german_html = f"<b>{item['german']}</b>"
            if item['plural']:
                german_html += f"<br/><font color='#64748b' size='7.5'>Pl: {item['plural']}</font>"

            trans_html = f"<font color='#0284c7'>[{item['transcription']}]</font><br/>{item['russian']}"
            example_html = f"<b>{item['example']}</b><br/><font color='#475569'>{item['example_translation']}</font>"

            table_data.append([
                Paragraph(str(item['number']), body_style),
                Paragraph(german_html, t_style),
                Paragraph(trans_html, body_style),
                Paragraph(example_html, example_style)
            ])

        t = Table(table_data, colWidths=[24, 155, 164, 180], repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

    # Section with Dialogues
    story.append(PageBreak())
    story.append(Paragraph("Готовые фразы и диалоги на линии (Sprechmuster am Band)", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceBefore=2, spaceAfter=8))

    phrases = [
        ("Просьба показать или объяснить", [
            ("«Entschuldigung, können Sie mir bitte kurz zeigen, wie das geht?»", "Извините, вы не могли бы мне коротко показать, как это делается?"),
            ("«Könnten Sie das bitte etwas langsamer wiederholen? Mein Deutsch ist noch nicht perfekt.»", "Не могли бы вы повторить немного медленнее? Мой немецкий пока не идеален."),
            ("«Habe ich das so richtig verstanden?»", "Я правильно это понял?"),
            ("«Ist das so in Ordnung oder soll ich etwas ändern?»", "Так в порядке или мне что-то изменить?")
        ]),
        ("Принятие задачи от бригадира", [
            ("«Alles klar, verstanden! Ich kümmere mich sofort darum.»", "Все ясно, понял! Я позабочусь об этом прямо сейчас."),
            ("«Kein Problem, das mache ich gerne.»", "Без проблем, я с удовольствием сделаю это."),
            ("«Soll ich hier die Packungen einlegen oder die Kartons auf die Palette stapeln?»", "Мне здесь закладывать упаковки или складывать коробки на поддон?")
        ]),
        ("Сообщение о сбое или нехватке материалов", [
            ("«Stopp! Am Band 2 gibt es einen Stau!»", "Стоп! На второй ленте затор!"),
            ("«Die Folie ist gleich leer, wir brauchen eine neue Rolle!»", "Пленка почти закончилась, нам нужен новый рулон!"),
            ("«Die Kontrollwaage piept ständig. Ich glaube, das Gewicht stimmt nicht.»", "Контрольные весы постоянно пищат. Кажется, вес не сходится."),
            ("«Der Kartonierer klemmt, die Kisten werden nicht transportiert!»", "Картониратор заклинило, коробки не двигаются!"),
            ("«Ich habe den Not-Aus-Schalter gedrückt, weil eine Schale feststeckt.»", "Я нажал аварийный стоп, потому что лоток застрял.")
        ]),
        ("Склад, тара и окончание смены", [
            ("«Wie viele Packungen kommen in diesen Karton?»", "Сколько упаковок идет в эту коробку?"),
            ("«Ist diese Palette fertig zum Einstretchen?»", "Этот поддон готов к обмотке пленкой?"),
            ("«Ich habe meinen Arbeitsplatz gründlich gereinigt und desinfiziert.»", "Я тщательно убрал и продезинфицировал свое рабочее место."),
            ("«Ich wünsche Ihnen einen schönen Feierabend! Bis morgen zur Frühschicht!»", "Желаю вам хорошего вечера! До завтра на утреннюю смену!")
        ])
    ]

    for p_cat, p_list in phrases:
        story.append(Paragraph(f"<b>{p_cat}</b>", cat_header_style))
        p_table_data = []
        for de, ru in p_list:
            p_table_data.append([
                Paragraph(f"<b>{de}</b>", term_style_blue),
                Paragraph(ru, body_style)
            ])
        pt = Table(p_table_data, colWidths=[270, 253])
        pt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(pt)
        story.append(Spacer(1, 8))

    # Tips for interview
    story.append(Spacer(1, 10))
    story.append(Paragraph("Советы для собеседования 21.10.2026 в JobImpulse", cat_header_style))
    tips_text = (
        "<b>1. Про отсутствие опыта наладки:</b> <i>«Ich habe bisher noch keine Verpackungsmaschinen selbstständig eingerichtet. "
        "Aber ich bin technisch geschickt, lerne sehr schnell und verstehe die Abläufe an der Linie gut. "
        "Als Helfer kann ich sofort beim Einlegen, Überwachen, Verpacken und bei der Qualitätskontrolle mit anpacken.»</i><br/><br/>"
        "<b>2. Про немецкий язык:</b> <i>«Mein Deutsch ist auf dem Niveau B1. Ich verstehe alle Arbeitsanweisungen und Fachbegriffe für die Linie gut. "
        "Wenn ich etwas nicht ganz verstehe, frage ich sofort nach, damit keine Fehler passieren.»</i><br/><br/>"
        "<b>3. Про смены и транспорт:</b> <i>«Ich bin voll schichtbereit für Früh-, Spät- und Nachtschicht. Ich wohne in Leonberg und bin in 15 Minuten in Ditzingen.»</i>"
    )
    tips_table = Table([[Paragraph(tips_text, body_style)]], colWidths=[523])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(tips_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built PDF: {pdf_path}")

if __name__ == '__main__':
    json_path = '/home/ubuntu/поиск работы в генмании/создание тренажера Немецкого/lebensmittel_produktion_wortschatz.json'
    pdf_path = '/home/ubuntu/поиск работы в генмании/создание тренажера Немецкого/Wortschatz_Lebensmittelproduktion_Ditzingen.pdf'
    build_pdf(json_path, pdf_path)
