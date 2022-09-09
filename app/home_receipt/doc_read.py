import pdfplumber
import re
from app.home_receipt.db_operations import Supplier, FilteredAddress, Bill
from app.home_receipt.models import db
from sqlalchemy import or_
from datetime import datetime, date

#pdf = pdfplumber.open("/Users/arnaudrover/PycharmProjects/s2pnl/app/static/1_Gaujac/bills/Devis SCHIRO MENUISERIES & FERMETURES - ROVER n°01860 2.pdf")

#first_page = pdf.pages[0]
#print(first_page.extract_text())
REGEX_RECEIPT = [["siret", r"siret[^\d]+(?P<siret>[\d ]+)"],
                 ["address", r"(?P<address>\d+.+(rue|avenue|av|impasse|imp|allée) [^\d]+)"],
                 ["postcode", r"[ \\n](?P<postcode>\d{5}) [^\n \d]{4,}"],
                 ["city", r"[ \\n](\d{5}) (?P<city>[^\n \d]{4,})"],
                 ["phone", r"(?P<phone>(\d{2}|\+\d{3})\.(\d{2}\.){3}\d{2})"],
                 # Phone format: 05 53 20 91 77
                 ["phone", r"(?P<phone>(\d{2}|\+\d{3}) (\d{2} ){3}\d{2})"],
                 ["email", r"(?P<email>[^ ]+@[^ .]+\.[^ \n]+)"],
                 ["date", r"(?P<date>(\d{2}/){2}\d{4})"],
                 ["total", r"total ttc[^\d]+(?P<total>([\d ]+[,\.]\d{2}))"]]

# Remove app folder in path file (app/static/project/file.pdf -> /static/project/file.pdf)
REGEX_FILE_PATH = r"^[^\/]+"


def extract_text(file):
    pdf = pdfplumber.open(file)
    text = ""
    if pdf is not None:
        for page in pdf.pages:
            text = text + page.extract_text()
    return text


def parse_bill(file, pj_id):
    text = extract_text(file).lower().replace(' ', ' ')
    result = {}
    supplier = None
    for param in REGEX_RECEIPT:
        result[param[0]] = result.get(param[0], [])
        matches = re.finditer(param[1], text, re.MULTILINE)
        for match in matches:
            if match.group(param[0]) not in result[param[0]]:
                result[param[0]].append(match.group(param[0]))
                # Try to find an existing supplier matching SIRET
                if param[0] == 'siret':
                    supplier = Supplier.query.filter_by(siret=match.group(param[0])).first()
                    if supplier is not None:
                        break
                # Try to find an existing supplier matching email
                if param[0] == 'email':
                    supplier = Supplier.query.filter_by(email=match.group(param[0])).first()
                    if supplier is not None:
                        break
                # Try to find an existing supplier matching address
                if param[0] == 'address':
                    supplier = Supplier.query.filter_by(address=match.group(param[0])).first()
                    if supplier is not None:
                        break
                # Try to find an existing supplier matching phone
                if param[0] == 'phone':
                    supplier = Supplier.query.filter_by(phone=match.group(param[0])).first()
                    if supplier is not None:
                        break
    if supplier is None:
        # If no existing supplier create a new one
        result['city'] = [city.upper() for city in result['city']]
        # Remove filtered addresses
        addresses = FilteredAddress.query.all()
        for filtered in addresses:
            result['address'] = list(filter(lambda ad: filtered.address.lower() not in ad.lower(), result['address']))
            result['phone'] = list(
                filter(lambda ad: filtered.address.lower().replace('.', '').replace(' ', '') not in ad.lower().replace('.', '').replace(' ', ''),
                       result['phone']))
            result['email'] = list(filter(lambda ad: filtered.address.lower() not in ad.lower(),
                                          result['email']))
        supplier = Supplier(name="", address=next(iter(result['address']), ""), email=next(iter(result['email']), ""),
                            postcode=next(iter(result['postcode']), ""), siret=next(iter(result['siret']), ""),
                            city=next(iter(result['address']), ""), phone=next(iter(result['phone']), ""))
        db.session.add(supplier)
        db.session.commit()
    result['total'] = [float(total.replace(',', '.').replace(' ', '')) for total in result['total']]
    # Sort total desc
    result['total'].sort(reverse=True)
    # Convert date to datetime
    result['date'] = list(map(lambda dt: datetime.strptime(dt, '%d/%m/%Y'), result['date']))
    bill = Bill(amount=next(iter(result['total']), 0), date=next(iter(result['date']), date.today()),
                file=re.sub(REGEX_FILE_PATH, "", file), supplier_id=supplier.id, project_id=pj_id,
                dtn_end_amort=next(iter(result['date']), date.today()))
    db.session.add(bill)
    db.session.commit()
    return bill

#print(parse_bill("/Users/arnaudrover/PycharmProjects/s2pnl/app/static/1_Gaujac/bills/Devis SCHIRO MENUISERIES & FERMETURES - ROVER n°01860 2.pdf"))