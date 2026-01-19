from fpdf import FPDF
from io import BytesIO
from datetime import datetime


def generate_pdf_report(client_name, stock_requirements, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "JRCL Steel Optimization Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Client Name: {client_name}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # Table 1: User Input
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "User Input", ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(40, 8, "Diameter", border=1)
    pdf.cell(40, 8, "Length (m)", border=1)
    pdf.cell(50, 8, "No. of Pieces", border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 12)
    for stock in stock_requirements:
        diameter = f"{stock['stock_diameter']} mm"
        for length, qty in stock["requirements"]:
            pdf.cell(40, 8, str(diameter), border=1)
            pdf.cell(40, 8, f"{length:.2f}", border=1)
            pdf.cell(50, 8, str(qty), border=1)
            pdf.ln()
    pdf.ln(5)

    # Table 2: Output Summary
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Optimization Summary", ln=True)
    for idx, stock in enumerate(stock_requirements):
        diameter = f"{stock['stock_diameter']} mm"
        result = results[idx]
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Stock Type {idx+1}: Diameter {diameter}", ln=True)
        pdf.set_font("Helvetica", "", 12)

        pdf.cell(80, 8, "Optimization Plan", border=1)
        pdf.cell(40, 8, "Value", border=1)
        pdf.ln()

        pdf.cell(80, 8, "No. of Bars", border=1)
        pdf.cell(40, 8, str(result['bars_used']), border=1)
        pdf.ln()

        pdf.cell(80, 8, "Total Weight", border=1)
        pdf.cell(40, 8, f"{result['total_weight_used'] + result['total_weight_wasted']:.2f} kg", border=1)
        pdf.ln()

        pdf.cell(80, 8, "Utilized Weight", border=1)
        pdf.cell(40, 8, f"{result['total_weight_used']:.2f} kg", border=1)
        pdf.ln()

        pdf.cell(80, 8, "Wasted Weight", border=1)
        pdf.cell(40, 8, f"{result['total_weight_wasted']:.2f} kg", border=1)
        pdf.ln()

        pdf.cell(80, 8, "Percentage Loss", border=1)
        pdf.cell(40, 8, f"{result['percent_loss']:.2f} %", border=1)
        pdf.ln(10)

    # Save PDF as string (fpdf returns bytes in Latin-1)
    pdf_str = pdf.output(dest='S').encode('latin1')  # <--- key fix
    pdf_buffer = BytesIO(pdf_str)
    pdf_buffer.seek(0)
    return pdf_buffer
