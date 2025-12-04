from core.utils.stribog import Stribog, hexdec, stribog_hex_to_str

if __name__ == "__main__":
    # 512
    m1 = hexdec(
        "323130393837363534333231303938373635343332313039383736353433323130393837363534333231303938373635343332313039383736353433323130"
    )[::-1]
    m1_hash = Stribog(m1).digest()
    m1_check = hexdec(
        "486f64c1917879417fef082b3381a4e211c324f074654c38823a7b76f830ad00fa1fbae42b1285c0352f227524bc9ab16254288dd6863dccd5b9f54a1ad0541b"
    )[::-1]
    
    print(m1_hash == m1_check)
    print(stribog_hex_to_str(m1))
    print(stribog_hex_to_str(m1_hash))
    print(stribog_hex_to_str(m1_check))
    # 256
    m1_hash_2 = Stribog(m1, digest_size=256).digest()
    m1_check_2 = hexdec("00557be5e584fd52a449b16b0251d05d27f94ab76cbaa6da890b59d8ef1e159d")[::-1]

    print(m1_hash_2 == m1_check_2)
    print(stribog_hex_to_str(m1_hash_2))
    print(stribog_hex_to_str(m1_check_2))