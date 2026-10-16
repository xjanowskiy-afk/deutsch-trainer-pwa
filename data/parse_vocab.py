import json
import re

md_path = '/home/ubuntu/поиск работы в генмании/создание тренажера Немецкого/Wortschatz_Lebensmittelproduktion_Ditzingen.md'
with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

items = []
current_item = None
current_category = ""
in_vocab_section = False

for line in lines:
    line_clean = line.strip()
    
    # Section starts at ## 1.
    if line_clean.startswith('## 1.'):
        in_vocab_section = True
        
    # Section ends before ## 9.
    if line_clean.startswith('## 9.'):
        in_vocab_section = False
        if current_item:
            items.append(current_item)
            current_item = None
        break

    if not in_vocab_section:
        continue

    if line_clean.startswith('## '):
        current_category = line_clean.replace('## ', '').strip()
        continue

    # Match numbered vocab: "1. 🔴 **die Verpackungsanlage** (Pl. *die Verpackungsanlagen*) `[ди фэрпа́кунгс-а́нлагэ]`"
    m_num = re.match(r'^(\d+)\.\s+(.*)', line_clean)
    if m_num:
        if current_item:
            items.append(current_item)
            current_item = None

        num = int(m_num.group(1))
        content = m_num.group(2)
        
        # remove emojis
        content_no_emoji = re.sub(r'[🔵🔴🟢🟠]', '', content).strip()
        
        # extract transcription: `[...]`
        transcription = ""
        m_tr = re.search(r'`\[(.*?)\]`', content_no_emoji)
        if m_tr:
            transcription = m_tr.group(1).strip()
            content_no_emoji = content_no_emoji.replace(m_tr.group(0), '').strip()
            
        # extract plural: (Pl. *...*)
        plural = ""
        m_pl = re.search(r'\(Pl\.\s+\*(.*?)\*\)', content_no_emoji)
        if m_pl:
            plural = m_pl.group(1).strip()
            content_no_emoji = content_no_emoji.replace(m_pl.group(0), '').strip()
        elif '(Plural)' in content_no_emoji or '(Pl.)' in content_no_emoji:
            plural = 'Plural'
            content_no_emoji = re.sub(r'\(Plural\)|\(Pl\.\)', '', content_no_emoji).strip()
        elif '(kein Pl.)' in content_no_emoji:
            plural = 'kein Plural'
            content_no_emoji = content_no_emoji.replace('(kein Pl.)', '').strip()
            
        # extract bold word
        m_bold = re.search(r'\*\*(.*?)\*\*', content_no_emoji)
        german_term = m_bold.group(1).strip() if m_bold else content_no_emoji
        
        # detect article and gender
        article = ""
        gender = ""
        if german_term.startswith('der '):
            article = 'der'
            gender = 'masculine'
        elif german_term.startswith('die '):
            article = 'die'
            gender = 'feminine' if plural != 'Plural' else 'plural'
        elif german_term.startswith('das '):
            article = 'das'
            gender = 'neuter'
            
        current_item = {
            "id": f"vocab-{num:03d}",
            "number": num,
            "german": german_term,
            "article": article,
            "gender": gender,
            "plural": plural,
            "transcription": transcription,
            "category": current_category,
            "russian": "",
            "example": "",
            "example_translation": ""
        }
        continue

    if current_item:
        if line_clean.startswith('- **Перевод:**'):
            current_item['russian'] = line_clean.replace('- **Перевод:**', '').strip()
        elif line_clean.startswith('- **Пример:**'):
            ex_content = line_clean.replace('- **Пример:**', '').strip()
            m_ex = re.search(r'\*(.*?)\*', ex_content)
            if m_ex:
                current_item['example'] = m_ex.group(1).strip()
            else:
                current_item['example'] = ex_content
        elif line_clean.startswith('*(') and line_clean.endswith(')*'):
            current_item['example_translation'] = line_clean[2:-2].strip()

if current_item:
    items.append(current_item)

output_json = {
    "title": "Fachwortschatz Lebensmittelherstellung & Verpackung",
    "target_company": "Bürger GmbH & Co. KG (Ditzingen) via JobImpulse Süd GmbH",
    "candidate": "Roman Aleksieiev",
    "total_items": len(items),
    "items": items
}

out_path = '/home/ubuntu/поиск работы в генмании/создание тренажера Немецкого/lebensmittel_produktion_wortschatz.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)

print(f"Successfully exported {len(items)} items to {out_path}")
