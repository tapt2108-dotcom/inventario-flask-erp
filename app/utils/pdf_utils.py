from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Reporte de Sistema de Inventario', align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_table(self, header, data, col_widths):
        self.set_font('helvetica', 'B', 10)
        for val, width in zip(header, col_widths):
            self.cell(width, 10, val, border=1, align='C')
        self.ln()
        
        self.set_font('helvetica', '', 10)
        for row in data:
            for val, width in zip(row, col_widths):
                self.cell(width, 10, str(val), border=1, align='C')
            self.ln()

def generate_inventory_pdf(products):
    pdf = PDFReport()
    pdf.add_page()
    pdf.chapter_title(f'Reporte de Inventario - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    header = ['ID', 'Nombre', 'Cantidad', 'Precio ($)', 'Total ($)']
    col_widths = [15, 80, 25, 30, 30]
    
    data = []
    total_val = 0
    for p in products:
        row_total = p.quantity * (p.price_usd or 0)
        total_val += row_total
        data.append([
            str(p.id),
            p.name,
            str(p.quantity),
            f"{p.price_usd:.2f}" if p.price_usd else "0.00",
            f"{row_total:.2f}"
        ])
    
    pdf.add_table(header, data, col_widths)
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f"Valor Total del Inventario: ${total_val:.2f}", 0, 1, 'R')
    
    return pdf

def generate_sales_pdf(sales_data):
    pdf = PDFReport()
    pdf.add_page()
    pdf.chapter_title(f'Reporte de Ventas (Últimos 7 días) - {datetime.now().strftime("%Y-%m-%d")}')
    
    header = ['Fecha', 'Ventas ($)']
    col_widths = [50, 50]
    
    data = []
    # sales_data is expected to be {labels: [], values: []}
    for date, value in zip(sales_data['labels'], sales_data['values']):
        data.append([date, f"${value:.2f}"])
        
    pdf.add_table(header, data, col_widths)
    
    total_sales = sum(sales_data['values'])
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f"Total Ventas Periodo: ${total_sales:.2f}", 0, 1, 'L')
    
    return pdf
