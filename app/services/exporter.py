from fpdf import FPDF

class PDFExporter:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_page()

        # إضافة الخطوط DejaVu (لازم يكونوا في المسار ده)
        self.pdf.add_font('DejaVu', '', 'assets/fonts/DejaVuSans.ttf', uni=True)
        self.pdf.add_font('DejaVu', '', 'assets/fonts/DejaVuSans.ttf', uni=True)

        # الخط الأساسي
        self.pdf.set_font("DejaVu", '', 16)

    def add_title(self, title):
        self.pdf.set_font("DejaVu", '', 16)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        self.pdf.ln(10)

    def add_section(self, header, content):
        self.pdf.set_font("DejaVu", '', 12)
        self.pdf.cell(0, 10, header, ln=True)
        self.pdf.set_font("DejaVu", '', 11)
        if isinstance(content, list):
            for item in content:
                self.pdf.multi_cell(0, 8, f"- {item}")
        else:
            self.pdf.multi_cell(0, 8, content)
        self.pdf.ln(5)

    def add_modules(self, training_modules):
        self.pdf.set_font("DejaVu", '', 12)
        self.pdf.cell(0, 10, "Training Modules:", ln=True)
        self.pdf.set_font("DejaVu", '', 11)
        
        if not isinstance(training_modules, list) or len(training_modules) == 0:
            self.pdf.cell(0, 10, "No modules available.", ln=True)
            return

        for module in training_modules:
            if isinstance(module, dict) and all(k in module for k in ("title", "description", "estimated_minutes")):
                self.pdf.multi_cell(0, 10, f"{module['title']} — {module['estimated_minutes']} mins")
                self.pdf.multi_cell(0, 8, module['description'])
                self.pdf.ln(5)
            else:
                self.pdf.cell(0, 10, "⚠️ Invalid module structure.", ln=True)

    def output(self, filename):
        self.pdf.output(filename)
