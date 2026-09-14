import streamlit as st
import google.generativeai as genai
import docx
import io
import time

# Cấu hình giao diện
st.set_page_config(page_title="Dịch Thuật Y Khoa AI", page_icon="⚕️", layout="wide")
st.title("⚕️ Trợ Lý Dịch Thuật Y Khoa AI (Chế độ Tốc độ cao)")

# Cấu hình API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("Chưa cấu hình API Key trong Streamlit Secrets.")
    st.stop()

# Khởi tạo AI
try:
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception as e:
    st.error(f"Lỗi khởi tạo mô hình: {e}")
    st.stop()

st.info("⚡ Đã kích hoạt chế độ gộp đoạn (Batching) giúp tăng tốc độ dịch gấp 5 lần.")

ngon_ngu_nguon = st.selectbox("Chọn ngôn ngữ nguồn:", ["Tiếng Anh", "Tiếng Pháp", "Tiếng Đức"])
file_word = st.file_uploader("Tải lên file Word (.docx) của bạn:", type=["docx"])
nut_dich = st.button("Bắt đầu dịch và Giữ nguyên bố cục 🚀", use_container_width=True)

if nut_dich and file_word is not None:
    try:
        # 1. Đọc file Word gốc
        doc = docx.Document(file_word)
        
        # Lọc ra những đoạn văn có chứa chữ (bỏ qua dòng trống hoặc chỉ có dấu cách)
        cac_doan_van_co_chu = [p for p in doc.paragraphs if p.text.strip() != ""]
        tong_so_doan = len(cac_doan_van_co_chu)
        
        if tong_so_doan == 0:
            st.warning("File Word của bạn không có chữ nào để dịch.")
        else:
            st.write(f"📂 Tìm thấy {tong_so_doan} đoạn văn bản. Đang áp dụng kỹ thuật gộp đoạn (Batching)...")
            thanh_tien_do = st.progress(0)
            
            # BATCH_SIZE: Số lượng đoạn văn sẽ gộp chung trong 1 lần gửi (Không nên để quá lớn để tránh AI bị "ngợp")
            BATCH_SIZE = 5 
            
            # 2. Vòng lặp gộp đoạn và xử lý
            for i in range(0, tong_so_doan, BATCH_SIZE):
                batch = cac_doan_van_co_chu[i : i + BATCH_SIZE]
                
                # Nối các đoạn văn lại bằng ký hiệu đặc biệt "|||"
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
                    # Tách bản dịch trả về dựa vào ký hiệu "|||"
                    ban_dich_cac_doan = response.text.split("|||")
                    
                    # Gán lại từng đoạn dịch vào đúng vị trí của file Word
                    for idx, para in enumerate(batch):
                        if idx < len(ban_dich_cac_doan):
                            para.text = ban_dich_cac_doan[idx].strip()
                        else:
                            para.text = f"[LỖI: AI bị sót đoạn này]"
                except Exception as e:
                    for para in batch:
                        para.text = f"[LỖI KẾT NỐI AI]"
                
                # Cập nhật thanh tiến độ
                tien_do_hien_tai = min((i + BATCH_SIZE) / tong_so_doan, 1.0)
                thanh_tien_do.progress(tien_do_hien_tai)
                
                # Cho ứng dụng nghỉ 2 giây để tránh bị Google chặn API vì gửi quá nhanh
                time.sleep(2)
            
            st.success("🎉 Đã dịch xong toàn bộ tài liệu ở tốc độ cao!")
            
            # 3. Đóng gói file Word mới để người dùng tải về
            output = io.BytesIO()
            doc.save(output)
            
            st.download_button(
                label="📥 Bấm vào đây để TẢI FILE ĐÃ DỊCH VỀ MÁY",
                data=output.getvalue(),
                file_name="Ban_Dich_Y_Khoa_Nhanh.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi đọc file: {e}")
        
elif nut_dich and file_word is None:
    st.warning("Vui lòng tải lên một file Word trước khi bấm dịch!")
