import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from sepaxml import SepaTransfer
import datetime
from re import sub
from schwifty import IBAN, BIC
import io
import json

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
            try:
                bic_obj = BIC(bic_str + "XXX")
            except:
                pass
        
    return str(bic_obj) if bic_obj else ""

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            df = pd.read_excel(file)
            columns = df.columns.tolist()
            df_json = df.to_json(orient='split', date_format='iso')
            
            heuristics = {
                "name": ["name", "recipient", "payee", "empfänger", "begünstigter"],
                "iban": ["iban"],
                "bic": ["bic", "swift"],
                "amount": ["amount", "value", "betrag", "summe"],
                "description": ["description", "purpose", "verwendungszweck", "zweck"]
            }
            
            suggested_mapping = {}
            for field, keywords in heuristics.items():
                for i, col in enumerate(columns):
                    if any(k in col.lower() for k in keywords):
                        suggested_mapping[field] = col
                        break
            
            return render_template('mapping.html', columns=columns, suggested=suggested_mapping, df_json=df_json)

    @app.route('/preview', methods=['POST'])
    def preview():
        df_json = request.form.get('df_json')
        df = pd.read_json(io.StringIO(df_json), orient='split')
        
        mapping = {
            "name": request.form.get('mapping_name'),
            "iban": request.form.get('mapping_iban'),
            "bic": request.form.get('mapping_bic'),
            "amount": request.form.get('mapping_amount'),
            "description": request.form.get('mapping_description')
        }
        
        sender_info = {
            "name": request.form.get('sender_name'),
            "iban": request.form.get('sender_iban').strip(),
            "bic": request.form.get('sender_bic').strip(),
            "execution_date": request.form.get('execution_date')
        }

        # Basic Sender Validation
        try:
            IBAN(sender_info['iban'])
            BIC(sender_info['bic'])
        except Exception as e:
            return f"Invalid Sender Data: {e}", 400
        
        session['mapping'] = mapping
        session['sender_info'] = sender_info
        
        preview_data = []
        total_sum_cents = 0
        
        for _, row in df.iterrows():
            try:
                amount_cents = clean_amount(row[mapping['amount']])
                total_sum_cents += amount_cents
                
                # Only add first 10 to preview list
                if len(preview_data) < 10:
                    preview_data.append({
                        "name": str(row[mapping['name']]),
                        "iban": str(row[mapping['iban']]),
                        "amount": f"{amount_cents/100:.2f}",
                        "description": str(row[mapping['description']])
                    })
            except:
                continue
                
        return render_template('preview.html', 
                               preview_data=preview_data, 
                               count=len(df), 
                               total_sum=f"{total_sum_cents/100:.2f}",
                               df_json=df_json)

    @app.route('/generate', methods=['POST'])
    def generate():
        df_json = request.form.get('df_json')
        mapping = session.get('mapping')
        sender_info = session.get('sender_info')
        
        if not df_json or not mapping or not sender_info:
            return redirect(url_for('index'))
        
        df = pd.read_json(io.StringIO(df_json), orient='split')
        
        config = {
            "name": sender_info['name'],
            "IBAN": sender_info['iban'],
            "BIC": sender_info['bic'],
            "batch": True,
            "currency": "EUR",
        }
        
        sepa = SepaTransfer(config, clean=True)
        
        exec_date = sender_info['execution_date']
        execution_date = datetime.date.today()
        if exec_date:
            try:
                execution_date = datetime.datetime.strptime(exec_date, "%Y-%m-%d").date()
            except:
                pass
        
        for _, row in df.iterrows():
            try:
                raw_iban = str(row[mapping['iban']]).strip()
                iban_obj = IBAN(raw_iban)
                
                raw_bic = ""
                if mapping['bic'] and mapping['bic'] in row and pd.notna(row[mapping['bic']]):
                    raw_bic = str(row[mapping['bic']]).strip()
                
                bic_str = derive_bic(raw_iban, raw_bic)
                amount_cents = clean_amount(row[mapping['amount']])
                
                payment = {
                    "name": str(row[mapping['name']]),
                    "IBAN": iban_obj.compact,
                    "BIC": bic_str,
                    "amount": amount_cents,
                    "execution_date": execution_date,
                    "description": str(row[mapping['description']]),
                }
                sepa.add_payment(payment)
            except:
                continue

        xml_data = sepa.export(validate=True)
        return send_file(
            io.BytesIO(xml_data),
            as_attachment=True,
            download_name="sepa_transfer.xml",
            mimetype="application/xml"
        )
    
    return app

def main():
    app = create_app()
    app.run(debug=False, port=5000)

if __name__ == '__main__':
    main()