"""Generate HIQ Data Sharing Agreement PDFs (English + French)."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT_DIR = os.path.expanduser("~/Desktop/HIQ_PDFs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HIQ_BLUE  = colors.HexColor("#1a3a5c")
HIQ_GOLD  = colors.HexColor("#c9a84c")
HIQ_LIGHT = colors.HexColor("#f4f6f9")
GREY_TEXT = colors.HexColor("#555555")


def base_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("HIQTitle",
        fontName="Helvetica-Bold", fontSize=22, textColor=HIQ_BLUE,
        spaceAfter=4, alignment=TA_CENTER, leading=28))
    s.add(ParagraphStyle("HIQSubtitle",
        fontName="Helvetica", fontSize=11, textColor=HIQ_GOLD,
        spaceAfter=2, alignment=TA_CENTER))
    s.add(ParagraphStyle("HIQDate",
        fontName="Helvetica", fontSize=9, textColor=GREY_TEXT,
        spaceAfter=14, alignment=TA_CENTER))
    s.add(ParagraphStyle("SectionHead",
        fontName="Helvetica-Bold", fontSize=12, textColor=HIQ_BLUE,
        spaceBefore=14, spaceAfter=4, leading=16))
    s.add(ParagraphStyle("Body",
        fontName="Helvetica", fontSize=9.5, textColor=colors.black,
        spaceBefore=2, spaceAfter=4, leading=14, alignment=TA_JUSTIFY))
    s.add(ParagraphStyle("BulletBody",
        fontName="Helvetica", fontSize=9.5, textColor=colors.black,
        spaceBefore=1, spaceAfter=2, leading=14,
        leftIndent=14, firstLineIndent=-14, alignment=TA_JUSTIFY))
    s.add(ParagraphStyle("SigLabel",
        fontName="Helvetica-Bold", fontSize=9, textColor=HIQ_BLUE,
        spaceBefore=2, spaceAfter=1))
    s.add(ParagraphStyle("SigLine",
        fontName="Helvetica", fontSize=9, textColor=GREY_TEXT,
        spaceBefore=0, spaceAfter=6))
    return s


def header_block(s, title, subtitle, ref, date_str):
    items = []
    items.append(Spacer(1, 6*mm))
    # Gold rule top
    items.append(HRFlowable(width="100%", thickness=3, color=HIQ_GOLD, spaceAfter=6))
    items.append(Paragraph("HospitalityIQ", s["HIQTitle"]))
    items.append(Paragraph(subtitle, s["HIQSubtitle"]))
    items.append(HRFlowable(width="100%", thickness=1, color=HIQ_GOLD, spaceBefore=6, spaceAfter=6))
    items.append(Paragraph(f"Ref: {ref} &nbsp;&nbsp;|&nbsp;&nbsp; {date_str}", s["HIQDate"]))
    return items


def sig_table(s, party_a_label, party_b_label):
    col_style = [
        Paragraph(party_a_label, s["SigLabel"]),
        Spacer(1, 14*mm),
        Paragraph("Signature: ___________________________", s["SigLine"]),
        Paragraph("Name: ________________________________", s["SigLine"]),
        Paragraph("Title: ________________________________", s["SigLine"]),
        Paragraph("Date: ________________________________", s["SigLine"]),
    ]
    col_style2 = [
        Paragraph(party_b_label, s["SigLabel"]),
        Spacer(1, 14*mm),
        Paragraph("Signature: ___________________________", s["SigLine"]),
        Paragraph("Name: ________________________________", s["SigLine"]),
        Paragraph("Title: ________________________________", s["SigLine"]),
        Paragraph("Date: ________________________________", s["SigLine"]),
    ]
    tbl = Table([[col_style, col_style2]], colWidths=["48%", "48%"],
                hAlign="CENTER", spaceBefore=8)
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tbl


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY_TEXT)
    canvas.drawString(20*mm, 12*mm, "HospitalityIQ — Confidential & Proprietary")
    canvas.drawRightString(A4[0] - 20*mm, 12*mm, f"Page {doc.page}")
    canvas.setStrokeColor(HIQ_GOLD)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 16*mm, A4[0] - 20*mm, 16*mm)
    canvas.restoreState()


# ─── ENGLISH ──────────────────────────────────────────────────────────────────

def build_english():
    s = base_styles()
    path = os.path.join(OUTPUT_DIR, "HIQ_Data_Sharing_Agreement.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=18*mm, bottomMargin=22*mm)

    story = []
    story += header_block(s,
        "HospitalityIQ",
        "DATA SHARING AGREEMENT",
        "HIQ-DSA-2026-001",
        "Effective Date: 1 June 2026")

    def sec(num, title):
        story.append(Paragraph(f"{num}. {title}", s["SectionHead"]))

    def body(text):
        story.append(Paragraph(text, s["Body"]))

    def bullet(text):
        story.append(Paragraph(f"• &nbsp; {text}", s["BulletBody"]))

    story.append(Spacer(1, 4*mm))
    body("This Data Sharing Agreement (<b>\"Agreement\"</b>) is entered into as of 1 June 2026 by and between:")
    story.append(Spacer(1, 2*mm))
    body("<b>HospitalityIQ</b> (\"HIQ\"), a market intelligence platform specialising in the Moroccan hospitality sector, registered under applicable laws of the Kingdom of Morocco, hereinafter referred to as the <b>\"Data Provider\"</b>;")
    body("and")
    body("<b>[Recipient Organisation Name]</b>, a company/institution duly incorporated and operating under the laws of <b>[Jurisdiction]</b>, with registered address at <b>[Address]</b>, hereinafter referred to as the <b>\"Data Recipient\"</b>.")

    story.append(HRFlowable(width="100%", thickness=0.5, color=HIQ_LIGHT, spaceBefore=8, spaceAfter=4))

    sec(1, "PURPOSE")
    body("The purpose of this Agreement is to establish the terms and conditions under which HIQ will share hotel market intelligence data, analytics, benchmarks, and related insights (collectively, the <b>\"Data\"</b>) with the Data Recipient for the specific use case(s) described herein.")

    sec(2, "SCOPE OF DATA")
    body("The Data shared under this Agreement may include, but is not limited to:")
    bullet("Hotel performance metrics: occupancy rates, Average Daily Rate (ADR), Revenue per Available Room (RevPAR), Total Revenue per Available Room (TRevPAR), and Gross Operating Profit (GOP) margins.")
    bullet("Hotel inventory data: property names, locations, categories, brand affiliations, room counts, and opening dates across the Kingdom of Morocco.")
    bullet("Pipeline intelligence: development projects, investment volumes, expected opening timelines, and market entry intelligence.")
    bullet("Tourism statistics: international arrivals, overnight stays by origin market, and airport traffic data.")
    bullet("News and market commentary produced by HIQ analysts.")

    sec(3, "PERMITTED USE")
    body("The Data Recipient is authorised to use the Data solely for the following purposes:")
    bullet("Internal business analysis, strategic planning, and investment decision-making.")
    bullet("Academic or research publications, subject to prior written consent from HIQ.")
    bullet("Regulatory reporting where required by applicable law, provided that HIQ is notified in advance.")
    body("The Data Recipient shall <b>not</b> use the Data for any purpose not expressly set out above without prior written approval from HIQ.")

    sec(4, "RESTRICTIONS")
    body("The Data Recipient agrees that it shall not, and shall ensure that its authorised personnel shall not:")
    bullet("Resell, redistribute, sublicense, or otherwise make the Data available to any third party without the express written consent of HIQ.")
    bullet("Reverse-engineer, decompile, or attempt to derive the underlying methodologies, algorithms, or source data from the Data.")
    bullet("Remove, alter, or obscure any proprietary notices, watermarks, or attributions contained in or accompanying the Data.")
    bullet("Use the Data in any manner that violates applicable laws, regulations, or professional standards.")

    sec(5, "INTELLECTUAL PROPERTY")
    body("All Data, analyses, reports, and derived works created by HIQ remain the exclusive intellectual property of HospitalityIQ. This Agreement confers no transfer of ownership, copyright, or any other intellectual property right to the Data Recipient. Any derived works or analyses created by the Data Recipient using the Data shall be clearly attributed to HIQ as the source.")

    sec(6, "CONFIDENTIALITY")
    body("The Data Recipient shall treat all Data as strictly confidential. It shall implement appropriate technical and organisational measures to prevent unauthorised access, disclosure, or use of the Data. The confidentiality obligation shall survive the termination of this Agreement for a period of five (5) years.")
    body("Exceptions to confidentiality obligations apply only where the Data Recipient can demonstrate that the information: (a) was already in the public domain prior to disclosure; (b) was independently developed without reference to the Data; or (c) is required to be disclosed by law or court order, subject to prompt advance notice to HIQ.")

    sec(7, "DATA SECURITY")
    body("The Data Recipient shall maintain commercially reasonable security standards to protect the Data, including but not limited to:")
    bullet("Access controls limiting Data access to authorised personnel on a need-to-know basis.")
    bullet("Encryption of Data at rest and in transit where technically feasible.")
    bullet("Prompt notification to HIQ within 72 hours of discovering any actual or suspected data breach involving the Data.")

    sec(8, "TERM AND TERMINATION")
    body("This Agreement shall commence on the Effective Date and remain in force for a period of one (1) year, unless earlier terminated. Either party may terminate this Agreement upon 30 days' written notice. HIQ may terminate immediately in the event of a material breach by the Data Recipient.")
    body("Upon termination, the Data Recipient shall promptly destroy or return all copies of the Data in its possession and certify such destruction in writing to HIQ within 10 business days.")

    sec(9, "WARRANTIES AND DISCLAIMER")
    body("HIQ warrants that it has the right to share the Data as contemplated by this Agreement. The Data is provided <b>\"as is\"</b> for informational purposes. HIQ makes no representations or warranties regarding the completeness, accuracy, or fitness for a particular purpose of the Data. HIQ shall not be liable for any loss, damage, or decision made in reliance on the Data.")

    sec(10, "GOVERNING LAW AND DISPUTE RESOLUTION")
    body("This Agreement shall be governed by and construed in accordance with the laws of the Kingdom of Morocco. Any dispute arising out of or in connection with this Agreement shall first be subject to good-faith negotiation between the parties. If unresolved within 30 days, disputes shall be referred to the competent courts of Casablanca, Morocco.")

    sec(11, "ENTIRE AGREEMENT")
    body("This Agreement constitutes the entire agreement between the parties with respect to the subject matter herein and supersedes all prior discussions, representations, or agreements. Amendments must be in writing and signed by authorised representatives of both parties.")

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=HIQ_GOLD, spaceAfter=8))
    story.append(Paragraph("SIGNATURES", s["SectionHead"]))
    body("By signing below, the parties agree to be bound by the terms of this Data Sharing Agreement.")
    story.append(Spacer(1, 4*mm))
    story.append(sig_table(s,
        "FOR HospitalityIQ (Data Provider)",
        "FOR [Recipient Organisation] (Data Recipient)"))

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return path


# ─── FRENCH ───────────────────────────────────────────────────────────────────

def build_french():
    s = base_styles()
    path = os.path.join(OUTPUT_DIR, "HIQ_Convention_Partage_Donnees.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=18*mm, bottomMargin=22*mm)

    story = []
    story += header_block(s,
        "HospitalityIQ",
        "CONVENTION DE PARTAGE DE DONNÉES",
        "HIQ-CPD-2026-001",
        "Date d'entrée en vigueur : 1er juin 2026")

    def sec(num, title):
        story.append(Paragraph(f"{num}. {title}", s["SectionHead"]))

    def body(text):
        story.append(Paragraph(text, s["Body"]))

    def bullet(text):
        story.append(Paragraph(f"• &nbsp; {text}", s["BulletBody"]))

    story.append(Spacer(1, 4*mm))
    body("La présente Convention de Partage de Données (<b>« Convention »</b>) est conclue en date du 1er juin 2026 entre :")
    story.append(Spacer(1, 2*mm))
    body("<b>HospitalityIQ</b> (« HIQ »), plateforme de veille stratégique spécialisée dans le secteur hôtelier marocain, constituée conformément aux lois applicables du Royaume du Maroc, ci-après désignée le <b>« Fournisseur de données »</b> ;")
    body("et")
    body("<b>[Nom de l'organisation destinataire]</b>, société/institution dûment constituée et opérant sous les lois de <b>[Juridiction]</b>, dont le siège social est situé à <b>[Adresse]</b>, ci-après désignée le <b>« Destinataire des données »</b>.")

    story.append(HRFlowable(width="100%", thickness=0.5, color=HIQ_LIGHT, spaceBefore=8, spaceAfter=4))

    sec(1, "OBJET")
    body("La présente Convention a pour objet de définir les termes et conditions dans lesquels HIQ communiquera au Destinataire des données des informations d'intelligence de marché hôtelier, des analyses, des benchmarks et des indicateurs connexes (collectivement, les <b>« Données »</b>) aux fins d'utilisation décrites aux présentes.")

    sec(2, "PÉRIMÈTRE DES DONNÉES")
    body("Les Données communiquées dans le cadre de la présente Convention peuvent comprendre, sans s'y limiter :")
    bullet("Indicateurs de performance hôtelière : taux d'occupation, tarif journalier moyen (ADR), revenu par chambre disponible (RevPAR), revenu total par chambre disponible (TRevPAR) et marges de résultat brut d'exploitation (GOP).")
    bullet("Inventaire hôtelier : dénomination des établissements, localisations, catégories, affiliations de marques, capacités en chambres et dates d'ouverture dans l'ensemble du Royaume du Maroc.")
    bullet("Intelligence du pipeline : projets de développement, volumes d'investissement, calendriers d'ouverture prévisionnels et renseignements sur les nouvelles entrées de marché.")
    bullet("Statistiques touristiques : arrivées internationales, nuitées par marché émetteur et trafic aéroportuaire.")
    bullet("Actualités et commentaires de marché produits par les analystes HIQ.")

    sec(3, "UTILISATION AUTORISÉE")
    body("Le Destinataire des données est autorisé à utiliser les Données exclusivement aux fins suivantes :")
    bullet("Analyse interne, planification stratégique et prise de décision d'investissement.")
    bullet("Publications académiques ou de recherche, sous réserve d'accord écrit préalable de HIQ.")
    bullet("Reporting réglementaire requis par la loi applicable, sous réserve de notification préalable à HIQ.")
    body("Le Destinataire des données <b>ne devra pas</b> utiliser les Données à des fins autres que celles expressément prévues ci-dessus sans l'approbation écrite préalable de HIQ.")

    sec(4, "RESTRICTIONS")
    body("Le Destinataire des données s'engage à ne pas, et à s'assurer que son personnel habilité ne :")
    bullet("Revendre, redistribuer, sous-licencier ou mettre les Données à disposition d'un tiers sans le consentement écrit exprès de HIQ.")
    bullet("Procéder à l'ingénierie inverse, décompiler ou tenter de déduire les méthodologies, algorithmes ou données sources sous-jacentes des Données.")
    bullet("Supprimer, modifier ou masquer les mentions de propriété, filigranes ou attributions contenus dans les Données ou les accompagnant.")
    bullet("Utiliser les Données d'une manière contraire aux lois, réglementations ou normes professionnelles applicables.")

    sec(5, "PROPRIÉTÉ INTELLECTUELLE")
    body("L'ensemble des Données, analyses, rapports et œuvres dérivées créés par HIQ demeurent la propriété intellectuelle exclusive de HospitalityIQ. La présente Convention ne confère aucun transfert de propriété, de droit d'auteur ou de tout autre droit de propriété intellectuelle au Destinataire des données. Toute œuvre dérivée créée par le Destinataire à partir des Données devra clairement mentionner HIQ comme source.")

    sec(6, "CONFIDENTIALITÉ")
    body("Le Destinataire des données traitera l'ensemble des Données comme strictement confidentielles. Il mettra en œuvre des mesures techniques et organisationnelles appropriées pour prévenir tout accès, divulgation ou utilisation non autorisés des Données. L'obligation de confidentialité survivra à la résiliation de la présente Convention pendant une durée de cinq (5) ans.")
    body("Les exceptions aux obligations de confidentialité s'appliquent uniquement lorsque le Destinataire peut démontrer que l'information : (a) était déjà dans le domaine public avant la divulgation ; (b) a été développée indépendamment sans référence aux Données ; ou (c) doit être divulguée par obligation légale ou ordonnance judiciaire, sous réserve d'un préavis rapide à HIQ.")

    sec(7, "SÉCURITÉ DES DONNÉES")
    body("Le Destinataire des données maintiendra des normes de sécurité raisonnables pour protéger les Données, incluant notamment :")
    bullet("Contrôles d'accès limitant l'accès aux Données au personnel habilité selon le principe du besoin d'en connaître.")
    bullet("Chiffrement des Données au repos et en transit dans la mesure du techniquement faisable.")
    bullet("Notification rapide à HIQ dans les 72 heures suivant la découverte de toute violation avérée ou suspectée impliquant les Données.")

    sec(8, "DURÉE ET RÉSILIATION")
    body("La présente Convention prend effet à la date d'entrée en vigueur et demeure en vigueur pour une durée d'un (1) an, sauf résiliation anticipée. Chaque partie peut résilier la Convention moyennant un préavis écrit de 30 jours. HIQ peut résilier immédiatement en cas de manquement grave du Destinataire.")
    body("À l'issue de la Convention, le Destinataire devra promptement détruire ou restituer tous les exemplaires des Données en sa possession et certifier par écrit ladite destruction à HIQ dans les 10 jours ouvrables.")

    sec(9, "GARANTIES ET CLAUSE DE NON-RESPONSABILITÉ")
    body("HIQ garantit qu'il dispose du droit de communiquer les Données conformément à la présente Convention. Les Données sont fournies <b>« en l'état »</b> à titre informatif. HIQ ne donne aucune garantie quant à l'exhaustivité, l'exactitude ou l'adéquation des Données à un usage particulier. HIQ ne saurait être tenu responsable de toute perte, dommage ou décision pris sur la base des Données.")

    sec(10, "DROIT APPLICABLE ET RÉSOLUTION DES LITIGES")
    body("La présente Convention est régie et interprétée conformément aux lois du Royaume du Maroc. Tout différend découlant de la présente Convention ou en lien avec celle-ci fera l'objet d'une négociation de bonne foi entre les parties. À défaut de résolution dans les 30 jours, les litiges seront portés devant les tribunaux compétents de Casablanca, Maroc.")

    sec(11, "INTÉGRALITÉ DE L'ACCORD")
    body("La présente Convention constitue l'accord intégral entre les parties concernant son objet et remplace toutes discussions, représentations ou accords antérieurs. Toute modification doit être établie par écrit et signée par les représentants habilités des deux parties.")

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=HIQ_GOLD, spaceAfter=8))
    story.append(Paragraph("SIGNATURES", s["SectionHead"]))
    body("En signant ci-dessous, les parties s'engagent à respecter les termes de la présente Convention de Partage de Données.")
    story.append(Spacer(1, 4*mm))
    story.append(sig_table(s,
        "POUR HospitalityIQ (Fournisseur de données)",
        "POUR [Organisation destinataire] (Destinataire des données)"))

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return path


if __name__ == "__main__":
    en = build_english()
    fr = build_french()
    print(f"English: {en}")
    print(f"French:  {fr}")
