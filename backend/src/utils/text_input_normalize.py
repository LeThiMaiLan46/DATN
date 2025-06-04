import re

# Your abbreviation mapping
ABBREVIATIONS = [
    ("gs", "giáo sư"),
    ("pgs", "phó giáo sư"),
    ("ts", "tiến sĩ"),
    ("ths", "thạc sĩ"),
    ("ks", "kỹ sư"),
    ("bs", "bác sĩ"),
    ("cn", "cử nhân"),
    ("nsnd", "nghệ sĩ nhân dân"),
    ("nsưt", "nghệ sĩ ưu tú"),
    ("ds", "dược sĩ"),
    ("ttnd", "thầy thuốc nhân dân"),
    ("ttưt", "thầy thuốc ưu tú"),
    ("ubnd", "ủy ban nhân dân"),
    ("hđnd", "hội đồng nhân dân"),
    ("byt", "bộ y tế"),
    ("bgdđt", "bộ giáo dục và đào tạo"),
    ("bca", "bộ công an"),
    ("bqp", "bộ quốc phòng"),
    ("btp", "bộ tư pháp"),
    ("blđtbxh", "bộ lao động thương binh và xã hội"),
    ("bvhttdl", "bộ văn hóa thể thao và du lịch"),
    ("btnmt", "bộ tài nguyên và môi trường"),
    ("ttcp", "thanh tra chính phủ"),
    ("vksndtc", "viện kiểm sát nhân dân tối cao"),
    ("tandtc", "tòa án nhân dân tối cao"),
    ("đhqg", "đại học quốc gia"),
    ("đhbk", "đại học bách khoa"),
    ("đhkt", "đại học kinh tế"),
    ("đhkhtn", "đại học khoa học tự nhiên"),
    ("đhkxh&nv", "đại học khoa học xã hội và nhân văn"),
    ("đhsp", "đại học sư phạm"),
    ("đhnn", "đại học ngoại ngữ"),
    ("đhktqd", "đại học kinh tế quốc dân"),
    ("hvbc&tt", "học viện báo chí và tuyên truyền"),
    ("hvn", "học viện ngoại giao"),
    ("hvch", "học viện cảnh sát"),
    ("tp", "thành phố"),
    ("tphcm", "thành phố hồ chí minh"),
    ("hn", "hà nội"),
    ("hp", "hải phòng"),
    ("đn", "đà nẵng"),
    ("ct", "cần thơ"),
    ("bd", "bình dương"),
    ("bn", "bắc ninh"),
    ("hcm", "hồ chí minh"),
    ("cmnd", "chứng minh nhân dân"),
    ("cccd", "căn cước công dân"),
    ("qđ", "quyết định"),
    ("tt", "thông tư"),
    ("nđ", "nghị định"),
    ("cv", "công văn"),
    ("gcnđkdn", "giấy chứng nhận đăng ký doanh nghiệp"),
    ("gcnqsđđ", "giấy chứng nhận quyền sử dụng đất"),
    ("gplđ", "giấy phép lao động"),
    ("nxb", "nhà xuất bản"),
    ("tw", "trung ương"),
    ("tnhh", "trách nhiệm hữu hạn"),
    ("cp", "cổ phần"),
    ("ctcp", "công ty cổ phần"),
    ("ctttnhh", "công ty trách nhiệm hữu hạn"),
    ("thpt", "trung học phổ thông"),
    ("thcs", "trung học cơ sở"),
    ("qh", "quốc hội"),
    ("dbqh", "đại biểu quốc hội"),
    ("bhyt", "bảo hiểm y tế"),
    ("bhxh", "bảo hiểm xã hội"),
    ("bhtn", "bảo hiểm thất nghiệp"),
    ("gtgt", "giá trị gia tăng"),
    ("tncn", "thu nhập cá nhân"),
    ("hđlđ", "hợp đồng lao động"),
    ("xhcn", "xã hội chủ nghĩa"),
    ("vnch", "việt nam cộng hòa"),
    ("chxhcnvn", "cộng hòa xã hội chủ nghĩa việt nam"),
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

def normalize_text(text):
    """
    Normalize text: strip, lowercase, expand abbreviations, and clean spacing.
    """
    # Strip leading/trailing whitespace
    text = text.strip()

    # Expand abbreviations (first without dot, then with dot to catch all cases)
    text = expand_abbreviations(text, with_dot=False)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    # Convert to lowercase
    text = text.lower()

    return text