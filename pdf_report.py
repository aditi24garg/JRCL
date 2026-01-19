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

    start_y = pdf.get_y()
    left_x = 10
    right_x = 110   # Adjust if needed

    # ---------------- LEFT: USER INPUT ----------------
    pdf.set_xy(left_x, start_y)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(90, 8, "User Input", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_x(left_x)
    pdf.cell(30, 8, "Diameter", border=1)
    pdf.cell(30, 8, "Length", border=1)
    pdf.cell(30, 8, "Qty", border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 11)

    left_table_y = pdf.get_y()

    for stock in stock_requirements:
        diameter = f"{stock['stock_diameter']} mm"
        for length, qty in stock["requirements"]:
            pdf.set_x(left_x)
            pdf.cell(30, 8, diameter, border=1)
            pdf.cell(30, 8, f"{length:.2f}", border=1)
            pdf.cell(30, 8, str(qty), border=1)
            pdf.ln()

    # ---------------- RIGHT: OPTIMIZATION SUMMARY ----------------
    pdf.set_xy(right_x, start_y)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(90, 8, "Optimization Summary", ln=True)

    for idx, stock in enumerate(stock_requirements):
        result = results[idx]
        diameter = f"{stock['stock_diameter']} mm"

        pdf.set_x(right_x)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(90, 8, f"Stock {idx+1} - {diameter}", ln=True)

        pdf.set_font("Helvetica", "", 11)

        rows = [
            ("No. of Bars", result['bars_used']),
            ("Total Weight", f"{result['total_weight_used'] + result['total_weight_wasted']:.2f} kg"),
            ("Utilized Weight", f"{result['total_weight_used']:.2f} kg"),
            ("Wasted Weight", f"{result['total_weight_wasted']:.2f} kg"),
            ("Loss %", f"{result['percent_loss']:.2f}%")
        ]

        for label, value in rows:
            pdf.set_x(right_x)
            pdf.cell(50, 8, label, border=1)
            pdf.cell(40, 8, str(value), border=1)
            pdf.ln()

        pdf.ln(4)

    # Output
    pdf_str = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_str)
    pdf_buffer.seek(0)
    return pdf_buffer