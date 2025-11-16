import csv
import os
import logging
from fpdf import FPDF

class Exporters:
    @staticmethod
    def to_csv(articles, filepath):
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Title', 'Keywords', 'Summary', 'URL'])
                for article in articles:
                    writer.writerow([
                        article.get('category', 'N/A'),
                        article.get('title', 'N/A'),
                        ', '.join(article.get('keywords', [])),
                        article.get('summary', 'N/A'),
                        article.get('url', 'N/A')
                    ])
            logging.info(f"Exported to CSV: {filepath}")
        except Exception as e:
            logging.error(f"Failed to export to CSV: {e}")

    @staticmethod
    def to_txt(articles, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for article in articles:
                    f.write(f"## {article.get('title', 'N/A')}\n")
                    f.write(f"- Category: {article.get('category', 'N/A')}\n")
                    f.write(f"- Keywords: {', '.join(article.get('keywords', []))}\n")
                    f.write(f"- URL: {article.get('url', 'N/A')}\n\n")
                    f.write(f"{article.get('summary', 'N/A')}\n")
                    f.write("-" * 20 + "\n\n")
            logging.info(f"Exported to TXT: {filepath}")
        except Exception as e:
            logging.error(f"Failed to export to TXT: {e}")

    @staticmethod
    def to_pdf(articles, filepath):
        # IMPORTANT: This requires a Korean-supporting TTF font file.
        # Download from https://hangeul.naver.com/font and place it in the 'fonts' directory.
        font_path = './fonts/NanumGothic.ttf'

        if not os.path.exists(font_path):
            logging.error(f"Font file not found at {font_path}. Cannot export PDF with Korean characters.")
            # Fallback or error message could be implemented here.
            return
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Add and set the Korean font
            pdf.add_font('NanumGothic', '', font_path, uni=True)
            pdf.set_font('NanumGothic', '', 12)

            for article in articles:
                pdf.set_font('NanumGothic', 'B', 14) # Title in Bold
                pdf.multi_cell(0, 10, article.get('title', 'N/A'))
                
                pdf.set_font('NanumGothic', '', 10)
                pdf.cell(0, 10, f"Category: {article.get('category', 'N/A')}", ln=1)
                pdf.cell(0, 10, f"Keywords: {', '.join(article.get('keywords', []))}", ln=1)
                pdf.cell(0, 10, f"URL: {article.get('url', 'N/A')}", ln=1)
                
                pdf.set_font('NanumGothic', '', 12)
                pdf.multi_cell(0, 10, article.get('summary', 'N/A'))
                pdf.ln(10) # Add some space

            pdf.output(filepath)
            logging.info(f"Exported to PDF: {filepath}")
        except Exception as e:
            logging.error(f"Failed to export to PDF: {e}")
