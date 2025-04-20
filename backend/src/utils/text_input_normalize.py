import re

# Your abbreviation mapping
ABBREVIATIONS = [
    # Format: ("Abbreviation", "Full form")
    ("GS", "Giáo sư"),
    ("PGS", "Phó Giáo sư"),
    ("TS", "Tiến sĩ"),
    ("ThS", "Thạc sĩ"),
    ("KS", "Kỹ sư"),
    ("BS", "Bác sĩ"),
    ("CN", "Cử nhân"),
    ("NSND", "Nghệ sĩ nhân dân"),
    ("NSƯT", "Nghệ sĩ ưu tú"),
    ("DS", "Dược sĩ"),
    ("TTND", "Thầy thuốc nhân dân"),
    ("TTƯT", "Thầy thuốc ưu tú"),
    ("UBND", "Ủy ban Nhân dân"),
    ("HĐND", "Hội đồng Nhân dân"),
    ("BYT", "Bộ Y tế"),
    ("BGDĐT", "Bộ Giáo dục và Đào tạo"),
    ("BCA", "Bộ Công an"),
    ("BQP", "Bộ Quốc phòng"),
    ("BTP", "Bộ Tư pháp"),
    ("BLĐTBXH", "Bộ Lao động Thương binh và Xã hội"),
    ("BVHTTDL", "Bộ Văn hóa Thể thao và Du lịch"),
    ("BTNMT", "Bộ Tài nguyên và Môi trường"),
    ("TTCP", "Thanh tra Chính phủ"),
    ("VKSNDTC", "Viện Kiểm sát nhân dân tối cao"),
    ("TANDTC", "Tòa án nhân dân tối cao"),
    ("ĐHQG", "Đại học Quốc gia"),
    ("ĐHBK", "Đại học Bách khoa"),
    ("ĐHKT", "Đại học Kinh tế"),
    ("ĐHKHTN", "Đại học Khoa học Tự nhiên"),
    ("ĐHKHXH&NV", "Đại học Khoa học Xã hội và Nhân văn"),
    ("ĐHSP", "Đại học Sư phạm"),
    ("ĐHNN", "Đại học Ngoại ngữ"),
    ("ĐHKTQD", "Đại học Kinh tế Quốc dân"),
    ("HVBC&TT", "Học viện Báo chí và Tuyên truyền"),
    ("HVN", "Học viện Ngoại giao"),
    ("HVCH", "Học viện Cảnh sát"),
    ("TP", "Thành phố"),
    ("TPHCM", "Thành phố Hồ Chí Minh"),
    ("HN", "Hà Nội"),
    ("HP", "Hải Phòng"),
    ("ĐN", "Đà Nẵng"),
    ("CT", "Cần Thơ"),
    ("BD", "Bình Dương"),
    ("BN", "Bắc Ninh"),
    ("HCM", "Hồ Chí Minh"),
    ("CMND", "Chứng minh nhân dân"),
    ("CCCD", "Căn cước công dân"),
    ("QĐ", "Quyết định"),
    ("TT", "Thông tư"),
    ("NĐ", "Nghị định"),
    ("CV", "Công văn"),
    ("GCNĐKDN", "Giấy chứng nhận đăng ký doanh nghiệp"),
    ("GCNQSDĐ", "Giấy chứng nhận quyền sử dụng đất"),
    ("GPLĐ", "Giấy phép lao động"),
    ("NXB", "Nhà xuất bản"),
    ("TW", "Trung ương"),
    ("TNHH", "Trách nhiệm hữu hạn"),
    ("CP", "Cổ phần"),
    ("CTCP", "Công ty cổ phần"),
    ("CTTTNHH", "Công ty trách nhiệm hữu hạn"),
    ("THPT", "Trung học phổ thông"),
    ("THCS", "Trung học cơ sở"),
    ("QH", "Quốc hội"),
    ("ĐBQH", "Đại biểu Quốc hội"),
    ("BHYT", "Bảo hiểm y tế"),
    ("BHXH", "Bảo hiểm xã hội"),
    ("BHTN", "Bảo hiểm thất nghiệp"),
    ("GTGT", "Giá trị gia tăng"),
    ("TNCN", "Thu nhập cá nhân"),
    ("HĐLĐ", "Hợp đồng lao động"),
    ("XHCN", "Xã hội chủ nghĩa"),
    ("VNCH", "Việt Nam Cộng hòa"),
    ("CHXHCNVN", "Cộng hòa Xã hội Chủ nghĩa Việt Nam"),
]

def expand_abbreviations(text, with_dot=True):
    """
    Replace abbreviations with their full form in the given text.
    
    Args:
        text (str): Input text containing abbreviations.
        with_dot (bool): If True, matches "ABBR." only. If False, matches "ABBR" with/without dot.

    Returns:
        str: Modified text with expanded abbreviations.
    """
    for abbr, full in ABBREVIATIONS:
        if with_dot:
            pattern = re.compile(r"\b%s\." % re.escape(abbr), re.IGNORECASE)
        else:
            pattern = re.compile(r"\b%s\.?" % re.escape(abbr), re.IGNORECASE)

        text = pattern.sub(full, text)

    return text
