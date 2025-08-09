import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Thay nội dung CLIENTE", layout="centered")
st.title("🔄 Thay toàn bộ nội dung dưới CLIENTE trong PDF")

# Nội dung mới muốn thay
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
    replaced_count = 0

    for page in doc:
        blocks = page.get_text("blocks")  # Mỗi block là (x0, y0, x1, y1, text, block_no, block_type)
        for idx, b in enumerate(blocks):
            text = b[4].strip()
            if text.startswith("CLIENTE:"):
                # Xác định vùng cần xóa: block hiện tại + một số block liền kề bên dưới (có thể chỉnh tùy PDF)
                y_top = b[1]
                y_bottom = b[3]

                # Lấy thêm 4 block phía dưới (tránh bỏ sót địa chỉ dài)
                for next_b in blocks[idx+1:idx+5]:
                    # Nếu block ở cùng cột và ngay dưới CLIENTE, thêm vào vùng xóa
                    if abs(next_b[0] - b[0]) < 5:  # so sánh cột
                        y_bottom = max(y_bottom, next_b[3])
                    else:
                        break

                # Xóa nội dung cũ
                rect = fitz.Rect(b[0], y_top, b[2] + 200, y_bottom)
                page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions()

                # Ghi nội dung mới vào đúng vùng
                page.insert_textbox(
                    rect,
                    new_text_block,
                    fontsize=8,       # chỉnh cho khớp
                    fontname="helv",  # giữ font gần giống
                    align=0
                )
                replaced_count += 1

    if replaced_count == 0:
        st.warning("⚠ Không tìm thấy CLIENTE trong PDF.")
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
