import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#6c757d'))
        
        if self._pageNumber > 1:
            # Running Header
            self.drawString(54, 11 * inch - 36, 'AgriPredict AI — Project Presentation & Viva Defense Guide')
            self.setStrokeColor(colors.HexColor('#e5e7eb'))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
        
        # Running Footer
        self.setStrokeColor(colors.HexColor('#e5e7eb'))
        self.setLineWidth(0.5)
        self.line(54, 45, 8.5 * inch - 54, 45)
        
        page_str = f'Page {self._pageNumber} of {page_count}'
        self.drawRightString(8.5 * inch - 54, 32, page_str)
        self.drawString(54, 32, 'Academic Project Defense Guide • AgriPredict Precision Agriculture Platform')
        self.restoreState()

def build_pdf():
    pdf_filename = 'AgriPredict_Project_Explanation_Guide.pdf'
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor('#1b4332')
    accent_color = colors.HexColor('#2d6a4f')
    text_dark = colors.HexColor('#1f2937')

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=23,
        leading=27,
        textColor=primary_color,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=accent_color,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=text_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3.5
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Title Banner
    story.append(Paragraph('🌾 AgriPredict AI Platform', title_style))
    story.append(Paragraph('Comprehensive Project Presentation, Website Walkthrough & Viva Defense Guide', subtitle_style))
    story.append(HRFlowable(width='100%', thickness=2, color=primary_color, spaceAfter=12))

    # Section 1: The 60-Second Elevator Pitch
    story.append(Paragraph('1. The 60-Second Elevator Pitch (Start Your Presentation Here)', h1_style))
    pitch_text = (
        "<b>What to say when introducing your project:</b><br/>"
        "<i>\"Respected professors and evaluators, <b>AgriPredict AI</b> is an end-to-end multi-modal precision "
        "agriculture system. By allowing farmers to upload a standard smartphone photograph of their field soil, "
        "the platform delivers four instantaneous intelligence layers without expensive in-ground sensors:<br/>"
        "<b>1. Optical Soil Texture Classification</b> (categorizing soil into physical classes).<br/>"
        "<b>2. Surface Moisture Estimation</b> (% Volumetric Water Content via Dark Channel Prior and radiometry).<br/>"
        "<b>3. Crop Yield Prediction</b> with 90% confidence uncertainty bounds.<br/>"
        "<b>4. Explainable AI (XAI)</b> diagnostics through Grad-CAM visual attention maps and SHAP feature attribution.<br/>"
        "Our goal is to democratize agricultural intelligence, cutting diagnostic latency from days to seconds.\"</i>"
    )

    t_callout = Table([[Paragraph(pitch_text, callout_style)]], colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ecfdf5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#10b981')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 8))

    # Section 2: Real-World Problem Statement
    story.append(Paragraph('2. Problem Statement & Motivation', h1_style))
    story.append(Paragraph('<b>Why does agriculture urgently need this platform?</b>', body_style))
    story.append(Paragraph('• <b>Laboratory Testing Bottlenecks:</b> Traditional laboratory chemical testing takes 3 to 7 days and costs $50-$200 per test, making timely advisory impossible for smallholders.', bullet_style))
    story.append(Paragraph('• <b>Irrigation Mismanagement:</b> Agriculture accounts for 70% of global freshwater withdrawals, yet 40-60% is wasted due to lack of topsoil moisture awareness.', bullet_style))
    story.append(Paragraph('• <b>IoT Sensor Limitations:</b> In-situ electronic moisture probes are fragile, expensive, and suffer from probe corrosion and battery depletion.', bullet_style))
    story.append(Paragraph('• <b>Black-Box Distrust:</b> Farmers often reject modern AI recommendations because traditional neural networks provide zero visual explanation for their decisions.', bullet_style))

    story.append(Spacer(1, 8))

    # Section 3: Architecture & Tech Stack
    story.append(Paragraph('3. System Architecture & Technology Stack', h1_style))
    story.append(Paragraph('AgriPredict employs a modern microservices architecture built for high throughput and low latency:', body_style))

    arch_data = [
        [Paragraph('<b>Layer</b>', body_style), Paragraph('<b>Technology</b>', body_style), Paragraph('<b>Role & Responsibility</b>', body_style)],
        [Paragraph('<b>Frontend UI</b>', body_style), Paragraph('Next.js 14, TypeScript, Tailwind CSS, Lucide, Recharts', body_style), Paragraph('Interactive playground, real-time image validation, yield analytics charts, What-If agronomic simulator, and voice advisory.', body_style)],
        [Paragraph('<b>ML Microservice</b>', body_style), Paragraph('FastAPI (Python 3.14), ONNX Runtime, PyTorch, OpenCV, Scikit-Learn', body_style), Paragraph('Computer vision pipeline, optical blur gating, CLAHE illumination correction, ONNX inference, and SHAP explainability.', body_style)],
        [Paragraph('<b>Backend & Gateway</b>', body_style), Paragraph('Spring Boot 3 (Java 21), Spring Security, Flyway, JPA', body_style), Paragraph('Enterprise gateway, JWT token authorization, farm/field relational data persistence, and REST client proxying.', body_style)],
        [Paragraph('<b>Data Layer</b>', body_style), Paragraph('PostgreSQL 16, Redis 7, MinIO (S3-compatible)', body_style), Paragraph('Relational state storage, sub-millisecond inference result caching, and soil image artifact repository.', body_style)],
    ]
    t_arch = Table(arch_data, colWidths=[95, 140, 269])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_arch)

    story.append(PageBreak())

    # Section 4: Live Website Demonstration Script
    story.append(Paragraph('4. Live Website Demonstration: Step-by-Step Script', h1_style))
    story.append(Paragraph('When demonstrating the website live on screen, follow these exact 7 steps:', body_style))

    steps_data = [
        [
            Paragraph('<b>Step 1: Crop & Field Setup</b>', h2_style),
            Paragraph('On the left panel, demonstrate selecting a crop (e.g., <i>Wheat, Rice, Maize, Cotton</i>). Show the <b>Settings Dialog</b> where field parameters (Nitrogen N, Phosphorus P, Potassium K, pH, and Rainfall) can be customized.', body_style)
        ],
        [
            Paragraph('<b>Step 2: Upload Soil Image</b>', h2_style),
            Paragraph('Drag and drop an image of field soil or select one of the pre-loaded samples. Explain: <i>\"Our frontend supports both direct camera photo uploads encoded as Base64 Data URIs and cloud URLs.\"</i>', body_style)
        ],
        [
            Paragraph('<b>Step 3: Click Analyze</b>', h2_style),
            Paragraph('Click <b>\"Analyze Soil & Predict Yield\"</b>. Point out the animated pipeline lifecycle tracker demonstrating optical validation, CLAHE lighting normalization, and tensor preparation.', body_style)
        ],
        [
            Paragraph('<b>Step 4: Soil Classification Card</b>', h2_style),
            Paragraph('Highlight the classified soil texture category (e.g., <i>Black Soil, Loamy, Cinder</i>) along with the confidence score and optical sharpness quality score (Laplacian blur rating).', body_style)
        ],
        [
            Paragraph('<b>Step 5: Moisture & Irrigation Advisory</b>', h2_style),
            Paragraph('Show the estimated Volumetric Water Content (% VWC) and the clear operational action message (e.g., <i>\"OPTIMAL - Adequate soil moisture\"</i> vs <i>\"HIGH - Immediate irrigation required within 24h\"</i>).', body_style)
        ],
        [
            Paragraph('<b>Step 6: Yield Prediction & Bounds</b>', h2_style),
            Paragraph('Point out the estimated yield in kg/ha. Emphasize the <b>confidence interval</b> [Lower - Upper], demonstrating that our system quantifies agricultural risk rather than giving a single naive number.', body_style)
        ],
        [
            Paragraph('<b>Step 7: Explainable AI & Simulator</b>', h2_style),
            Paragraph('Switch to the <b>Grad-CAM Viewer</b> and <b>Yield Analytics Chart</b>. Demonstrate the interactive What-If Simulator to show how modifying rainfall or fertilizer impacts projected yields in real time.', body_style)
        ],
    ]
    t_steps = Table(steps_data, colWidths=[140, 364])
    t_steps.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_steps)
    story.append(Spacer(1, 8))

    # Section 5: The 5-Stage Computer Vision & ML Pipeline
    story.append(Paragraph('5. The 5-Stage AI & Computer Vision Pipeline', h1_style))
    story.append(Paragraph('Explain the technical engineering under the hood with these 5 stages:', body_style))

    story.append(Paragraph('<b>Stage 1: Optical Clarity Filter (Laplacian Variance)</b>', h2_style))
    story.append(Paragraph('OpenCV computes the second derivative of image luminance: <i>Var(nabla^2 I)</i>. If blur score < 40.0, the photo is gated and rejected before running heavy deep learning models, protecting prediction integrity.', body_style))

    story.append(Paragraph('<b>Stage 2: Illumination Normalization (CLAHE)</b>', h2_style))
    story.append(Paragraph('Contrast Limited Adaptive Histogram Equalization operates on the L* channel in LAB color space to equalize outdoor sunlight variations and shadows without distorting soil color tone.', body_style))

    story.append(Paragraph('<b>Stage 3: Radiometric & GLCM Texture Extraction</b>', h2_style))
    story.append(Paragraph('Extracts Gray-Level Co-occurrence Matrix (GLCM) contrast, dissimilarity, homogeneity, and energy alongside Local Binary Patterns (LBP) to describe micro-granularity.', body_style))

    story.append(Paragraph('<b>Stage 4: ONNX Deep Learning Soil Texture Classifier</b>', h2_style))
    story.append(Paragraph('Executes an optimized MobileNetV3 convolutional network inside ONNX Runtime. Utilizing ONNX eliminates heavy framework runtime dependencies, slashing production memory by 60% and delivering sub-100ms CPU inference.', body_style))

    story.append(Paragraph('<b>Stage 5: Moisture Estimation & Yield Integration</b>', h2_style))
    story.append(Paragraph('Water absorption darkens soil reflectance according to optical physics. The Dark Channel Prior (DCP) inversely maps luminance to Volumetric Water Content (% VWC) in typical field capacity ranges (8% to 48%).', body_style))

    story.append(PageBreak())

    # Section 6: How to Defend Tough Evaluator & Viva Questions
    story.append(Paragraph('6. How to Defend Tough Evaluator & Viva Questions', h1_style))
    story.append(Paragraph('Academic evaluators respect technical honesty. Use these professionally framed defenses:', body_style))

    qa_list = [
        (
            'Q1: "Is the yield prediction really trained on live soil moisture and NPK sensor inputs?"',
            'Strong Academic Answer:',
            '\"In our current prototype, historical district production records (240,000+ data.gov.in rows) provide baseline yield bounds, while topsoil moisture, NPK, and pH modulate this baseline through an agronomic response curve with 90% confidence bounds. For our production roadmap, we plan to couple this with the ICAR / Soil Health Card soil chemical sensor dataset to train an end-to-end multi-modal gradient boosted model.\"'
        ),
        (
            'Q2: "Can a smartphone camera photo really replace a laboratory chemical soil test?"',
            'Strong Academic Answer:',
            '\"No, and that is a key distinction we highlight. AgriPredict does not claim to replace spectrometer-based chemical soil tests for trace micronutrients. Instead, it provides zero-hardware, instantaneous field screening for physical texture classification, surface moisture monitoring, and irrigation scheduling, cutting diagnostic latency from days to seconds.\"'
        ),
        (
            'Q3: "Why did you export the model to ONNX instead of running raw PyTorch in production?"',
            'Strong Academic Answer:',
            '\"ONNX provides hardware-independent graph optimization, removes PyTorch and CUDA runtime dependencies from production containers, decreases memory footprint by over 60%, and achieves sub-80ms CPU inference latency.\"'
        ),
        (
            'Q4: "What happens if a farmer uploads an image taken under harsh shadows or bad lighting?"',
            'Strong Academic Answer:',
            '\"We built a two-tiered defense: first, the Laplacian variance filter rejects images lacking optical focus; second, CLAHE contrast limiting in the L* channel prevents shadow saturation from corrupting texture descriptor extraction.\"'
        ),
        (
            'Q5: "How does the Explainable AI (XAI) feature benefit farmers?"',
            'Strong Academic Answer:',
            '\"Traditional AI is rejected by farmers because it behaves like an opaque black box. Our Grad-CAM heatmap highlights the exact soil pixel regions the model analyzed, while SHAP feature attributions show whether factors like nitrogen or soil moisture positively or negatively drove the yield forecast.\"'
        ),
    ]

    for q, h, a in qa_list:
        card_content = [
            [Paragraph(f'<b>{q}</b>', h2_style)],
            [Paragraph(f'<b>{h}</b><br/>{a}', body_style)]
        ]
        t_card = Table(card_content, colWidths=[504])
        t_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#ffffff')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_card)
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 6))

    # Section 7: Conclusion
    story.append(Paragraph('7. Closing Statement for Your Defense', h1_style))
    conclusion_text = (
        "<b>Final Presentation Takeaway:</b><br/>"
        "<i>\"In summary, AgriPredict AI bridges the critical gap between complex agricultural data science "
        "and practical on-field decision-making. By uniting computer vision preprocessing, ONNX runtime efficiency, "
        "and transparent Explainable AI within a farmer-friendly web portal, our project demonstrates a scalable, "
        "sustainable blueprint for modern digital agriculture. Thank you.\"</i>"
    )

    t_concl = Table([[Paragraph(conclusion_text, callout_style)]], colWidths=[504])
    t_concl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_concl)

    doc.build(story, canvasmaker=NumberedCanvas)
    print("SUCCESS: PDF compiled to", os.path.abspath(pdf_filename))

if __name__ == '__main__':
    build_pdf()
