import pytest
from re import sub
from schwifty import IBAN, BIC

def clean_amount(raw_amount):
    raw_amount = str(raw_amount).strip()
    if ',' in raw_amount and '.' in raw_amount:
        if raw_amount.find('.') < raw_amount.find(','):
            raw_amount = raw_amount.replace('.', '').replace(',', '.')
        else:
            raw_amount = raw_amount.replace(',', '')
    elif ',' in raw_amount:
        parts = raw_amount.split(',')
        if len(parts[-1]) <= 2:
            raw_amount = raw_amount.replace(',', '.')
        else:
            raw_amount = raw_amount.replace(',', '')
            
    clean = sub(r'[^\d.]', '', raw_amount)
    return int(round(float(clean) * 100))

def derive_bic(iban_str, provided_bic=None):
    iban_obj = IBAN(iban_str)
    bic_obj = None
    
    if provided_bic and str(provided_bic).strip():
        try:
            bic_obj = BIC(str(provided_bic).strip())
        except:
            pass
            
    if not bic_obj:
        bic_obj = iban_obj.bic
        
    if bic_obj and bic_obj.branch_code is None:
        bic_str = str(bic_obj)
        if len(bic_str) == 8:
            bic_obj = BIC(bic_str + "XXX")
        
    return str(bic_obj) if bic_obj else ""

def test_amount_cleaning():
    assert clean_amount("123,45") == 12345
    assert clean_amount("1.234,56") == 123456
    assert clean_amount("1,234.56") == 123456
    assert clean_amount("12.34") == 1234
    assert clean_amount(" 5 € ") == 500
    assert clean_amount("100") == 10000

def test_iban_bic_derivation():
    # German IBAN (Valid from Faker)
    de_iban = "DE14621656389698315367"
    bic = derive_bic(de_iban)
    assert isinstance(bic, str)
    
    # Dutch IBAN (Valid from Faker)
    nl_iban = "NL46HWQO9773240303"
    bic = derive_bic(nl_iban)
    assert isinstance(bic, str)
    
    # Test with provided BIC
    assert derive_bic(de_iban, "PBNKDEFF") == "PBNKDEFF"

def test_invalid_iban_error_handling():
    with pytest.raises(Exception):
        IBAN("FR7630006000011234567890101") # Wrong checksum
