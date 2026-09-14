import streamlit as st
import google.generativeai as genai
import docx
import io
import time

# Cấu hình giao diện
st.set_page_config(page_title="Dịch Thuật Y Khoa", page_icon="⚕️", layout="wide")
st.title("⚕️ Trợ Lý Dịch Thuật Y Khoa AI (Hỗ trợ file Word)")

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

st.info("💡 Mẹo: Hãy thử tải lên một file Word ngắn (1-2 trang) để kiểm tra độ giữ form trước khi dùng file lớn.")

ngon_ngu_nguon = st.selectbox("Chọn ngôn ngữ nguồn:", ["Tiếng Anh", "Tiếng Pháp", "Tiếng Đức"])
file_word = st.file_uploader("Tải lên file Word (.docx) của bạn:", type=["docx"])
nut_dich = st.button("Bắt đầu dịch và Giữ nguyên bố cục 🚀", use_container_width=True)

if nut_dich and file_word is not None:
    try:
        # 1. Đọc file Word gốc
        doc = docx.Document(file_word)
        
        # Lọc ra những đoạn văn có chứa chữ (bỏ qua dòng trống)
        cac_doan_van_co_chu = [p for p in doc.paragraphs if p.text.strip() != ""]
        tong_so_doan = len(cac_doan_van_co_chu)
        
        if tong_so_doan == 0:
            st.warning("File Word của bạn không có chữ nào để dịch.")
        else:
            st.write(f"📂 Tìm thấy {tong_so_doan} đoạn văn bản cần dịch. Đang xử lý...")
            thanh_tien_do = st.progress(0)
            
            # 2. Vòng lặp dịch từng đoạn và thay thế trực tiếp
            for i, para in enumerate(cac_doan_van_co_chu):
                text_goc = para.text
                
                prompt = f"""
                Dịch đoạn văn bản y khoa {ngon_ngu_nguon} sau sang Tiếng Việt.
                Chỉ trả về kết quả dịch, không giải thích gì thêm, giữ nguyên các thuật ngữ chuyên ngành.
                Văn bản gốc: {text_goc}
                """
                
                try:
                    # Gửi AI dịch
                    response = model.generate_content(prompt)
                    # Ghi đè bản dịch lên đúng vị trí cũ trong Word
                    para.text = response.text
                except Exception as e:
                    # Nếu có lỗi (như quá tải mạng), ghi nhận lại nhưng không làm sập ứng dụng
                    para.text = f"[LỖI DỊCH: {text_goc}]"
                
                # Cập nhật thanh tiến độ
                thanh_tien_do.progress((i + 1) / tong_so_doan)
                
                # Cực kỳ quan trọng: Nghỉ 2 giây để Google không khóa AI vì spam gửi liên tục
                time.sleep(2)
            
            st.success("🎉 Đã dịch xong toàn bộ tài liệu!")
            
            # 3. Đóng gói file Word mới để người dùng tải về
            output = io.BytesIO()
            doc.save(output)
            
            st.download_button(
                label="📥 Bấm vào đây để TẢI FILE ĐÃ DỊCH VỀ MÁY",
                data=output.getvalue(),
                file_name="Ban_Dich_Y_Khoa.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi đọc file: {e}")
        
elif nut_dich and file_word is None:
    st.warning("Vui lòng tải lên một file Word trước khi bấm dịch!")
