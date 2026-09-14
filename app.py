import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện trang web
st.set_page_config(page_title="Dịch Thuật Y Khoa", page_icon="⚕️", layout="wide")

st.title("⚕️ Trợ Lý Dịch Thuật Y Khoa AI")
st.markdown("Dịch tài liệu y văn từ Tiếng Anh, Pháp, Đức sang Tiếng Việt với độ chuẩn xác cao.")

# Lấy API Key bí mật từ cấu hình của Streamlit
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Chưa cấu hình API Key. Vui lòng thêm GOOGLE_API_KEY vào Streamlit Secrets.")
    st.stop()

# Cấu hình mô hình AI
model = genai.GenerativeModel('gemini-1.5-flash')

# Bố cục 2 cột: Trái (Nhập) - Phải (Kết quả)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Bản gốc")
    ngon_ngu_nguon = st.selectbox("Chọn ngôn ngữ nguồn:", ["Tiếng Anh", "Tiếng Pháp", "Tiếng Đức"])
    van_ban_goc = st.text_area("Dán đoạn văn bản y khoa vào đây:", height=300)
    nut_dich = st.button("Bắt đầu dịch 🚀", use_container_width=True)

with col2:
    st.subheader("Bản dịch (Tiếng Việt)")
    
    if nut_dich:
        if van_ban_goc.strip() == "":
            st.warning("Vui lòng nhập văn bản cần dịch!")
        else:
            with st.spinner('Đang dịch thuật, vui lòng chờ...'):
                # Viết Prompt chuyên sâu cho y khoa
                prompt = f"""
                Bạn là một bác sĩ chuyên khoa và biên dịch viên y khoa xuất sắc.
                Hãy dịch đoạn văn bản {ngon_ngu_nguon} sau sang Tiếng Việt.
                Yêu cầu:
                - Văn phong y khoa chuyên nghiệp, chính xác.
                - Giữ nguyên các danh pháp quốc tế (như tên thuốc, tên vi khuẩn) hoặc mở ngoặc chú thích nếu cần.
                - Nếu có từ viết tắt y khoa, hãy giải nghĩa nó.
                
                Đoạn văn bản:
                {van_ban_goc}
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("Dịch thành công!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
