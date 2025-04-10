import pandas as pd
import psycopg2

csv_path = '/Users/shahzeb/Desktop/projects/NeoLease/data/dtc_lease_results.csv'
df = pd.read_csv(csv_path)

# Rename columns (exactly as before)
df.columns = [
    "url", "title", "subtitle", "financial_lease_price", "financial_lease_term",
    "advertentienummer", "merk", "model", "bouwjaar", "km_stand",
    "transmissie", "prijs", "brandstof", "btw_marge", "opties_accessoires",
    "address", "images"
]

df = df.where(pd.notnull(df), None)

try:
    conn = psycopg2.connect(
        dbname='neolease_db',
        host='localhost',
        port=5432
    )
    cur = conn.cursor()

    for idx, row in df.iterrows():
        try:
            print(f"\nInserting row {idx}:\n{row}")  # Debug print

            cur.execute("""
                INSERT INTO car_listings (
                    url, title, subtitle, financial_lease_price, financial_lease_term,
                    advertentienummer, merk, model, bouwjaar, km_stand,
                    transmissie, prijs, brandstof, btw_marge, opties_accessoires,
                    address, images
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, tuple(row))

        except Exception as e:
            print(f"❌ Error on row {idx}: {e}")
            print("Offending row data:")
            print(row)
            break  # Stop so we can see exactly which row failed

    conn.commit()
    print("\n✅ Finished inserting rows!")

except Exception as e:
    print("\n❌ Overall connection or query error:")
    print(e)

finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
