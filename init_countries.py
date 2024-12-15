from database import init_db, db_session
from generated_models.country import Country

# List of countries with their ISO codes and regions
countries = [
    ("Canada", "CA", "North America"),
    ("Mexico", "MX", "North America"),
    ("United Kingdom", "GB", "Europe"),
    ("France", "FR", "Europe"),
    ("Germany", "DE", "Europe"),
    ("Italy", "IT", "Europe"),
    ("Spain", "ES", "Europe"),
    ("Portugal", "PT", "Europe"),
    ("Netherlands", "NL", "Europe"),
    ("Belgium", "BE", "Europe"),
    ("Switzerland", "CH", "Europe"),
    ("Austria", "AT", "Europe"),
    ("Sweden", "SE", "Europe"),
    ("Norway", "NO", "Europe"),
    ("Denmark", "DK", "Europe"),
    ("Finland", "FI", "Europe"),
    ("Japan", "JP", "Asia"),
    ("China", "CN", "Asia"),
    ("South Korea", "KR", "Asia"),
    ("India", "IN", "Asia"),
    ("Australia", "AU", "Oceania"),
    ("New Zealand", "NZ", "Oceania"),
    ("Brazil", "BR", "South America"),
    ("Argentina", "AR", "South America"),
    ("Chile", "CL", "South America"),
    ("Peru", "PE", "South America"),
    ("Colombia", "CO", "South America"),
    ("South Africa", "ZA", "Africa"),
    ("Egypt", "EG", "Africa"),
    ("Nigeria", "NG", "Africa"),
    ("Kenya", "KE", "Africa"),
    ("Morocco", "MA", "Africa"),
    ("Russia", "RU", "Europe/Asia"),
    ("Turkey", "TR", "Europe/Asia"),
    ("Israel", "IL", "Middle East"),
    ("Saudi Arabia", "SA", "Middle East"),
    ("UAE", "AE", "Middle East"),
    ("Singapore", "SG", "Asia"),
    ("Malaysia", "MY", "Asia"),
    ("Thailand", "TH", "Asia"),
]

def init_countries():
    # Add each country to the database
    for name, code, region in countries:
        country = Country()
        country.name = name
        country.code = code
        country.region = region
        db_session.add(country)
    
    # Commit all changes
    db_session.commit()

if __name__ == '__main__':
    init_countries()
    print(f"Successfully added {len(countries)} countries to the database.")
