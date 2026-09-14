import streamlit as st
import google.generativeai as genai
import pypdf

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

# Bố cục 2 cột: Trái (Nhập liệu) - Phải (Kết quả)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Nguồn tài liệu")
    ngon_ngu_nguon = st.selectbox("Chọn ngôn ngữ nguồn:", ["Tiếng Anh", "Tiếng Pháp", "Tiếng Đức"])
    
    # Tạo 2 Tab để người dùng dễ thao tác
    tab1, tab2 = st.tabs(["📄 Tải lên file PDF", "📝 Dán văn bản"])
    
    with tab1:
        file_pdf = st.file_uploader("Chọn file PDF từ máy tính của bạn:", type=["pdf"])
        st.caption("Ứng dụng sẽ tự động đọc và trích xuất chữ từ PDF để dịch.")
        
    with tab2:
        van_ban_nhap = st.text_area("Hoặc dán đoạn văn bản y khoa vào đây:", height=200)
        
    nut_dich = st.button("Bắt đầu dịch 🚀", use_container_width=True)

with col2:
    st.subheader("Bản dịch (Tiếng Việt)")
    
    if nut_dich:
        noidung_candich = ""
        
        # Ưu tiên xử lý file PDF nếu người dùng tải lên
        if file_pdf is not None:
            with st.spinner('Đang đọc file PDF...'):
                try:
                    # Dùng pypdf để đọc từng trang và lấy chữ
                    doc = pypdf.PdfReader(file_pdf)
                    for page in doc.pages:
                        text = page.extract_text()
                        if text:
                            noidung_candich += text + "\n"
                except Exception as e:
                    st.error(f"Không thể đọc file PDF: {e}")
        else:
            # Nếu không có file PDF, lấy dữ liệu từ ô nhập chữ
            noidung_candich = van_ban_nhap
            
        # Kiểm tra xem có dữ liệu để dịch chưa
        if noidung_candich.strip() == "":
            st.warning("Vui lòng tải lên một file PDF hoặc nhập văn bản!")
        else:
            with st.spinner('Đang dịch thuật, vui lòng chờ... (Có thể mất chút thời gian nếu tài liệu dài)'):
                # Khung lệnh (Prompt) yêu cầu AI dịch thuật
                prompt = f"""
                Bạn là một bác sĩ chuyên khoa và biên dịch viên y khoa xuất sắc.
                Hãy dịch nội dung {ngon_ngu_nguon} sau sang Tiếng Việt.
                Yêu cầu:
                - Văn phong y khoa chuyên nghiệp, chính xác.
                - Giữ nguyên các danh pháp quốc tế (như tên thuốc, tên vi khuẩn, hoạt chất) hoặc mở ngoặc chú thích nếu cần.
                - Nếu có từ viết tắt y khoa, hãy giải nghĩa nó.
                - Trình bày kết quả rõ ràng, chia đoạn hợp lý để dễ đọc.
                
                Nội dung cần dịch:
                {noidung_candich}
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("Dịch thành công!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Có lỗi xảy ra với AI: {e}")
