from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph


class PDFExporter:
    def generate_pdf(self, invoice_data):
        """Generate a PDF for the given invoice data."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Title
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Invoice #{invoice_data['id']}", styles["Title"]))

        # Customer Information
        elements.append(
            Paragraph(f"Customer: {invoice_data['customer']}", styles["Normal"])
        )
        elements.append(
            Paragraph(f"Invoice Date: {invoice_data['invoice_date']}", styles["Normal"])
        )

        # Table of services
        table_data = [
            [
                "Transaction ID",
                "Service",
                "Cost",
                "Close Date",
                "Reference Number",
                "Ship To Name",
                "Ship To Company",
                "Ship To Address",
                "Ship To Address2",
                "Ship To City",
                "Ship To State",
                "Ship To Zip",
                "Ship To Country",
                "Weight (lb)",
                "Line Items",
                "SKU Quantity",
                "Total Item Qty",
                "Volume (cuft)",
                "Packages",
                "Notes",
                "Carrier",
            ]
        ]
        for detail in invoice_data["details"]:
            table_data.append(
                [
                    detail["transaction_id"],
                    detail["service"],
                    f"${detail['cost']}",
                    detail["close_date"],
                    detail["reference_number"],
                    detail["ship_to_name"],
                    detail["ship_to_company"],
                    detail["ship_to_address"],
                    detail["ship_to_address2"],
                    detail["ship_to_city"],
                    detail["ship_to_state"],
                    detail["ship_to_zip"],
                    detail["ship_to_country"],
                    detail["weight_lb"],
                    detail["line_items"],
                    detail["sku_quantity"],
                    detail["total_item_qty"],
                    detail["volume_cuft"],
                    detail["packages"],
                    detail["notes"],
                    detail["carrier"],
                ]
            )

        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(table)

        # Total Amount
        elements.append(
            Paragraph(
                f"Total Amount: ${invoice_data['total_cost']}", styles["Heading2"]
            )
        )

        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf")
