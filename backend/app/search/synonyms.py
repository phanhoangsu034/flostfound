"""
Vietnamese synonym dictionary for search expansion.
Groups of related terms – if ANY term in a group matches the query,
all other terms in the same group are also searched.
"""

# Each list is a group of synonyms / related terms.
SYNONYM_GROUPS = [
    # Wallet / Purse
    ["ví", "bóp", "ví nam", "ví nữ", "ví da", "bóp da", "bóp nam", "bóp nữ"],
    # Student card
    ["thẻ sv", "thẻ sinh viên", "student card", "thẻ svien", "thẻ s.v"],
    # Phone
    ["điện thoại", "dt", "phone", "dien thoai", "iphone", "samsung", "oppo", "xiaomi"],
    # Keys
    ["chìa khóa", "chìa khoá", "chia khoa", "chìa", "key", "móc khóa", "móc chìa"],
    # Laptop / Computer
    ["laptop", "máy tính", "may tinh", "máy tính xách tay", "notebook", "macbook"],
    # Charger / Cable
    ["sạc", "cáp sạc", "sac", "dây sạc", "adapter", "củ sạc", "cục sạc"],
    # Backpack / Bag
    ["balo", "ba lô", "túi", "cặp", "túi xách", "cặp sách", "ba-lô"],
    # Headphones
    ["tai nghe", "headphone", "earphone", "airpods", "earbuds", "tay nghe"],
    # Glasses
    ["kính", "kính mắt", "kinh mat", "mắt kính", "glasses"],
    # Umbrella
    ["ô", "dù", "ô dù", "umbrella"],
    # Bottle
    ["bình nước", "chai nước", "binh nuoc", "chai", "bình giữ nhiệt"],
    # Card / ID
    ["thẻ", "thẻ ngân hàng", "thẻ atm", "cmnd", "cccd", "căn cước", "chứng minh"],
    # USB / Flash drive
    ["usb", "flash drive", "ổ cứng", "ổ đĩa", "thẻ nhớ", "memory card"],
    # Motorcycle helmet
    ["mũ bảo hiểm", "nón bảo hiểm", "mu bao hiem", "mũ", "nón"],
    # Money
    ["tiền", "tiền mặt", "tien", "cash"],
    # Clothing
    ["áo", "quần", "ao", "quan", "áo khoác", "jacket"],
    # Watch
    ["đồng hồ", "dong ho", "watch", "smartwatch"],
    # Vehicle card / Parking card
    ["thẻ xe", "the xe", "thẻ gửi xe", "vé xe"],
]


def _build_lookup():
    """Build a reverse lookup: term -> set of all related terms."""
    lookup = {}
    for group in SYNONYM_GROUPS:
        terms_set = set(t.lower() for t in group)
        for term in terms_set:
            lookup[term] = terms_set
    return lookup


_LOOKUP = _build_lookup()


def expand_query(query: str) -> list[str]:
    """
    Given a search query, return a list of expanded keywords.
    E.g. expand_query("bóp da") -> ["bóp da", "ví", "bóp", "ví nam", ...]
    """
    query_lower = query.lower().strip()
    expanded = {query_lower}

    # Check if the whole query matches a synonym
    if query_lower in _LOOKUP:
        expanded.update(_LOOKUP[query_lower])

    # Check individual words
    words = query_lower.split()
    for word in words:
        if word in _LOOKUP:
            expanded.update(_LOOKUP[word])

    # Check pairs of consecutive words  (e.g. "thẻ sv" in "tìm thẻ sv")
    for i in range(len(words) - 1):
        pair = f"{words[i]} {words[i+1]}"
        if pair in _LOOKUP:
            expanded.update(_LOOKUP[pair])

    return list(expanded)
