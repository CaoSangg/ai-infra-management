import os
import google.generativeai as genai
from dotenv import load_dotenv

def get_gemini_models():
    # Load biến môi trường từ file .env
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Lỗi: Không tìm thấy GOOGLE_API_KEY trong file .env")
        return

    # Cấu hình thư viện với API key của bạn
    genai.configure(api_key=api_key)

    print("=== DANH SÁCH CÁC MODEL GEMINI ===")
    print("Đang tải dữ liệu từ Google API...\n")
    
    try:
        # Gọi API để lấy danh sách các model
        models = genai.list_models()
        
        count = 0
        for m in models:
            # Chỉ lọc ra những model hỗ trợ tạo text (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"- Tên model: {m.name}")
                # In thêm mô tả ngắn gọn nếu có
                print(f"  Mô tả: {m.description}\n")
                count += 1
                
        print(f"Tổng cộng tìm thấy {count} model hỗ trợ tạo nội dung.")
        
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gọi API: {e}")

if __name__ == "__main__":
    get_gemini_models()
