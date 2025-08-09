import streamlit as st
import fitz  # PyMuPDF
import io
import re

st.set_page_config(page_title="Thay thế CLIENTE trong PDF", layout="centered")
st.title("🔄 Thay nội dung CLIENTE trong PDF (giữ font gần gốc)")

# Nội dung mới
new_text_block = """CLIENTE:
SUNFLOWER LOGISTIC SL
CALLE SANDALIO LOPEZ,20 ENTREGA 10-14H
MADRID, MADRID
28034 ESPAÑA
C.I.F.: B09775438"""

uploaded_file = st.file_uploader("📂 Tải PDF", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Regex tìm khối CLIENTE cũ
    pattern = re.compile(
        r"CLIENTE:\s+VIETCARE MADRID 2018 S\.L\s+C\.I\.F\.: B88166319\s+CALLE SANDALIO LOPEZ, 20\s+28034 SPAIN\s+MADRID, MADRID",
        re.MULTILINE
    )

    replaced_count = 0
    for page in doc:
        blocks = page.get_text("blocks")  # lấy các block text
        for b in blocks:
            text = b[4]
            if re.search(pattern, text):
                rect = fitz.Rect(b[0], b[1], b[2], b[3])
                # Xóa nội dung cũ
                page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions()
                # Thêm nội dung mới
                page.insert_textbox(
                    rect,
                    new_text_block,
                    fontsize=8,       # chỉnh font size khớp PDF
                    fontname="helv",  # PyMuPDF sẽ map sang font gần giống gốc
                    align=0
                )
                replaced_count += 1

    if replaced_count == 0:
        st.warning("⚠ Không tìm thấy khối CLIENTE cần thay.")
    else:
        output = io.BytesIO()
        doc.save(output)
        doc.close()

        st.success(f"✅ Đã thay thế {replaced_count} lần!")
        st.download_button(
            "⬇ Tải PDF đã chỉnh sửa",
            output.getvalue(),
            file_name="pdf_thay_the.pdf",
            mime="application/pdf"
        )
