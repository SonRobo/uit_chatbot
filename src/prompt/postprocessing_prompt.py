"""
This prompt for post processing.
"""

POST_PROCESS = """
{result}

## Nguồn thông tin
{source}
"""

SOURCE = """
### Tài liệu {idx}
{title_text}
{session_text}
{page_text}
{data_type_text}
{link_text}
"""

FAIL_CASES = [
    "Nội dung bạn đề cập không nằm trong phạm vi của nhà trường.",
    None,
    "None"
]

RESPONSE_FAIL_CASE = """
Xin chào! Rất tiếc, tôi chưa thể cung cấp thông tin mà bạn đang tìm kiếm vào lúc này. Nhưng đừng lo, tôi luôn sẵn sàng hỗ trợ bạn!

Để biết thêm thông tin chi tiết, bạn có thể liên hệ qua:

- **Hotline**: 090.883.1246
- **Website**: [tuyensinh.uit.edu.vn](https://tuyensinh.uit.edu.vn)

Cảm ơn bạn đã sử dụng dịch vụ của UITAdminBot! Nếu có thắc mắc khác, đừng ngần ngại hỏi tôi nhé.
"""

RESPONSE_UNSUPPORTED_LANGUAGE = """
Xin chào! Rất tiếc, Hệ thống tư vấn tuyển sinh của trường hiện tại không hỗ trợ ngôn ngữ mà bạn đang sử dụng. Hãy chắc rằng bạn sử dụng tiếng việt khi sử dụng chatbot bạn nhé!

Để biết thêm thông tin chi tiết, bạn có thể liên hệ qua:

- **Hotline**: 090.883.1246
- **Website**: [tuyensinh.uit.edu.vn](https://tuyensinh.uit.edu.vn)

Cảm ơn bạn đã sử dụng dịch vụ của UITAdminBot! Nếu có thắc mắc khác, đừng ngần ngại hỏi tôi nhé.
"""

RESPONSE_PROMPT_INJECTION = """
Xin chào! Hệ thống phát hiện bạn đang xử dụng ngôn từ chưa phù hợp với chính sách của nhà trường.

Để bảo đảm an toàn và trải nghiệm tốt nhất cho tất cả người dùng, xin vui lòng tuân thủ các hướng dẫn và quy định của nền tảng.

Nếu bạn có bất kỳ thắc mắc nào hoặc cần hỗ trợ, vui lòng liên hệ với đội ngũ hỗ trợ chatbot. Cảm ơn bạn đã hợp tác!

Trân trọng,

UITAdminBot
"""
