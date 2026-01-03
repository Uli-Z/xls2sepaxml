import pandas as pd
from xls2sepaxml.web import clean_amount, derive_bic
from schwifty import IBAN
import pytest

def test_process_generated_excel():
    df = pd.read_excel("international_test_data.xlsx")
    
    success_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            # 1. Test Amount Cleaning
            amt = clean_amount(row['Amount'])
            assert isinstance(amt, int)
            assert amt > 0
            
            # 2. Test IBAN Validation
            iban_str = str(row['IBAN']).strip()
            iban_obj = IBAN(iban_str)
            
            # 3. Test BIC Derivation
            # For random fake IBANs, schwifty might not find a real bank mapping.
            # We just want to ensure it doesn't crash and returns at least an empty string or BIC if found.
            bic = derive_bic(iban_str)
            assert isinstance(bic, str)
            
            success_count += 1
        except Exception as e:
            errors.append(f"Row {index} failed: {e} (Data: {row.to_dict()})")
    
    print(f"\nSuccessfully processed {success_count} / {len(df)} rows.")
    
    if errors:
        for err in errors:
            print(err)
        pytest.fail(f"Encountered {len(errors)} errors during processing")

if __name__ == "__main__":
    test_process_generated_excel()