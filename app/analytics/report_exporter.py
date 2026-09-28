import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportExporter:
    """Gerador local de relatórios executivos em PDF a custo zero."""

    @classmethod
    def generate_pdf_report(cls, title: str, content_markdown: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0284c7'), # Azul ciano corporativo
            spaceAfter=12
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=8
        )

        elements = []
        elements.append(Paragraph(f"AI-OmniRouter | Relatório Executivo Analítico", styles['Heading3']))
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 10))

        # Formata parágrafos limpos removendo marcações pesadas
        paragraphs = content_markdown.split("\n\n")
        for p in paragraphs:
            cleaned = p.replace("**", "<b>").replace("</b><b>", "").replace("```python", "").replace("```sql", "").replace("```", "")
            cleaned = cleaned.replace("---", "").strip()
            if cleaned:
                elements.append(Paragraph(cleaned, body_style))
                elements.append(Spacer(1, 4))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
