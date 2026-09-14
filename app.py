import streamlit as st
import google.generativeai as genai
import docx
import io
import time

# Cấu hình giao diện
st.set_page_config(page_title="Dịch Thuật Y Khoa AI", page_icon="⚕️", layout="wide")
st.title("⚕️ Trợ Lý Dịch Thuật Y Khoa AI (Chống Quá Tải)")

# Cấu hình API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("Chưa cấu hình API Key trong Streamlit Secrets.")
    st.stop()

# Khởi tạo mô hình AI
try:
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception as e:
    st.error(f"Lỗi khởi tạo mô hình AI: {e}")
    st.stop()

st.info("🛡️ Đã kích hoạt chế độ 'Chống Quá Tải': Xử lý chậm lại để đảm bảo an toàn cho các file dài, bỏ qua chú thích ảnh và bảng biểu.")

# Giao diện người dùng
ngon_ngu_nguon = st.selectbox("Chọn ngôn ngữ nguồn:", ["Tiếng Anh", "Tiếng Pháp", "Tiếng Đức"])
file_word = st.file_uploader("Tải lên file Word (.docx) của bạn:", type=["docx"])
nut_dich = st.button("Bắt đầu dịch 🚀", use_container_width=True)

if nut_dich and file_word is not None:
    try:
        doc = docx.Document(file_word)
        
        # Lọc các đoạn văn bản có chữ và bỏ qua định dạng Caption (Chú thích ảnh)
        cac_doan_van_co_chu = []
        for p in doc.paragraphs:
            if p.text.strip() != "" and p.style.name != 'Caption':
                cac_doan_van_co_chu.append(p)
                
        tong_so_doan = len(cac_doan_van_co_chu)
        
        if tong_so_doan == 0:
            st.warning("File Word không có đoạn văn bản thường nào để dịch.")
        else:
            st.write(f"📂 Tìm thấy {tong_so_doan} đoạn văn bản. Bắt đầu dịch an toàn (Sẽ mất thời gian với file dài)...")
            thanh_tien_do = st.progress(0)
            
            # CHỐNG QUÁ TẢI: Giảm số đoạn gộp xuống 3
            BATCH_SIZE = 3 
            
            for i in range(0, tong_so_doan, BATCH_SIZE):
                batch = cac_doan_van_co_chu[i : i + BATCH_SIZE]
                
                # Kẹp ký hiệu "|||" giữa các đoạn để AI phân biệt
                van_ban_gop = " \n\n|||\n\n ".join([p.text for p in batch])
                
                prompt = f"""
                Bạn là biên dịch viên y khoa chuyên nghiệp.
                Hãy dịch các đoạn văn bản {ngon_ngu_nguon} sau sang Tiếng Việt.
                Cực kỳ quan trọng: 
                - Các đoạn văn bản đang được ngăn cách bởi ký hiệu '|||'. 
                - Bạn PHẢI giữ nguyên ký hiệu '|||' giữa các đoạn bản dịch.
                - KHÔNG thêm bất kỳ lời bình luận hay giải thích nào.
                
                Nội dung cần dịch:
                {van_ban_gop}
                """
                
                try:
                    response = model.generate_content(prompt)
                    ban_dich_cac_doan = response.text.split("|||")
                    
                    for idx, para in enumerate(batch):
                        if idx < len(ban_dich_cac_doan):
                            para.text = ban_dich_cac_doan[idx].strip()
                        else:
                            para.text = f"[LỖI: AI bị sót đoạn này]"
                except Exception as e:
                    # Báo lỗi nhỏ gọn, không phá vỡ cỡ chữ gốc của tài liệu
                    for para in batch:
                        para.text = f"[Lỗi mạng nội bộ do quá tải API]"
                
                tien_do_hien_tai = min((i + BATCH_SIZE) / tong_so_doan, 1.0)
                thanh_tien_do.progress(tien_do_hien_tai)
                
                # CHỐNG QUÁ TẢI: Ép hệ thống nghỉ 8 giây giữa các lần gọi
                time.sleep(8)
            
            st.success("🎉 Đã dịch xong toàn bộ tài liệu!")
            
            # Xuất file
            output = io.BytesIO()
            doc.save(output)
            
            st.download_button(
                label="📥 Bấm vào đây để TẢI FILE ĐÃ DỊCH VỀ MÁY",
                data=output.getvalue(),
                file_name="Ban_Dich_Y_Khoa_An_Toan.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi đọc file: {e}")
        
elif nut_dich and file_word is None:
    st.warning("Vui lòng tải lên một file Word trước khi bấm dịch!")
