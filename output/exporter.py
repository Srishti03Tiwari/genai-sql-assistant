# output/exporter.py
import pandas as pd
import io
from fpdf import FPDF


def to_csv(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    return buffer.getvalue()


def to_pdf(df: pd.DataFrame, title: str = "Query Results") -> bytes:
    """Convert DataFrame to a formatted PDF bytes."""
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(4)

    if df.empty:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 10, "No results found.", ln=True)
        return bytes(pdf.output())

    # Auto column width
    num_cols  = len(df.columns)
    page_width = 270        # A4 landscape usable width in mm
    col_width  = min(page_width / num_cols, 60)

    # Header row — dark background, white text
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    for col in df.columns:
        pdf.cell(col_width, 8, str(col)[:20], border=1, fill=True, align="C")
    pdf.ln()

    # Data rows — alternating row colors
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    for i, row in df.iterrows():
        if i % 2 == 0:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        for val in row:
            pdf.cell(col_width, 7, str(val)[:25], border=1, fill=True, align="L")
        pdf.ln()

    return bytes(pdf.output())