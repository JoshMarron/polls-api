import json
from models import Company
from polls_api import db

with open('json_data/companies.json', 'r') as companies_file:
    companies = json.load(companies_file)

for company in companies:
    details = companies.get(company)

    code = details.get("code")
    name = details.get("name")
    canonical = details.get("canonical")
    url = details.get("url")

    company_model = Company(code=code, name=name, canonical=canonical, url=url)
    db.session.add(company_model)

db.session.commit()
