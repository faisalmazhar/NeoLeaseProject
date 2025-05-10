# import pandas as pd
# import psycopg2

# csv_path = '/Users/shahzeb/Desktop/projects/NeoLease/data/dtc_lease_results.csv'
# df = pd.read_csv(csv_path)

# # Rename columns (exactly as before)
# df.columns = [
#     "url", "title", "subtitle", "financial_lease_price", "financial_lease_term",
#     "advertentienummer", "merk", "model", "bouwjaar", "km_stand",
#     "transmissie", "prijs", "brandstof", "btw_marge", "opties_accessoires",
#     "address", "images"
# ]

# df = df.where(pd.notnull(df), None)

# try:
#     conn = psycopg2.connect(
#         dbname="neolease_db",
#         user="neolease_db_user",
#         password="DKuNZ0Z4OhuNKWvEFaAuWINgr7BfgyTE",
#         host="dpg-cvslkuvdiees73fiv97g-a.oregon-postgres.render.com",
#         port="5432"
#     )

#     cur = conn.cursor()

#     for idx, row in df.iterrows():
#         try:
#             print(f"\nInserting row {idx}:\n{row}")  # Debug print

#             cur.execute("""
#                 INSERT INTO car_listings (
#                     url, title, subtitle, financial_lease_price, financial_lease_term,
#                     advertentienummer, merk, model, bouwjaar, km_stand,
#                     transmissie, prijs, brandstof, btw_marge, opties_accessoires,
#                     address, images
#                 )
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
#             """, tuple(row))

#         except Exception as e:
#             print(f"❌ Error on row {idx}: {e}")
#             print("Offending row data:")
#             print(row)
#             break  # Stop so we can see exactly which row failed

#     conn.commit()
#     print("\n✅ Finished inserting rows!")

# except Exception as e:
#     print("\n❌ Overall connection or query error:")
#     print(e)

# finally:
#     if 'cur' in locals(): cur.close()
#     if 'conn' in locals(): conn.close()





import pandas as pd
import psycopg2

csv_path = '/Users/shahzeb/Desktop/projects/NeoLease/data/dtc_lease_results.csv'
df = pd.read_csv(csv_path)

# CSV columns
df.columns = [
    "url", "title", "subtitle", "financial_lease_price", "financial_lease_term",
    "advertentienummer", "merk", "model", "bouwjaar", "km_stand",
    "transmissie", "prijs", "brandstof", "btw_marge", "opties_accessoires",
    "address", "images"
]

# Convert NaN to None
df = df.where(pd.notnull(df), None)

def safe_int_str(value):
    """
    If value is numeric, return str(int(value)).
    Otherwise return None.
    """
    if value is None:
        return None
    try:
        return str(int(float(value)))
    except:
        return None

def trunc_str(value, max_len):
    """
    If `value` is a string longer than max_len, slice it.
    Otherwise return as is (or None).
    """
    if not value or not isinstance(value, str):
        return value
    if len(value) > max_len:
        return value[:max_len]
    return value

try:
    print("[DEBUG] Connecting to Render Postgres...")
    conn = psycopg2.connect(
        dbname="neolease_db_kpz9",
        user="neolease_db_kpz9_user",
        password="33H6QVFnAouvau72DlSjuKAMe5GdfviD",
        host="dpg-d0f0ihh5pdvs73b6h3bg-a.oregon-postgres.render.com",
        port="5432"
        # dbname="neolease_db",
        # user="neolease_db_user",
        # password="DKuNZ0Z4OhuNKWvEFaAuWINgr7BfgyTE",
        # host="dpg-cvslkuvdiees73fiv97g-a.oregon-postgres.render.com",
        # port="5432"
    )
    cur = conn.cursor()
    print("[DEBUG] Connected successfully.")

    for idx, row in df.iterrows():
        # Convert bouwjaar + km_stand
        bouwjaar_str = safe_int_str(row["bouwjaar"])
        kmstand_str  = safe_int_str(row["km_stand"])

        # Apply truncation to each relevant field
        url   = trunc_str(row["url"], 300)
        title = trunc_str(row["title"], 200)
        subt  = trunc_str(row["subtitle"], 200)
        flp   = trunc_str(row["financial_lease_price"], 100)
        flt   = trunc_str(row["financial_lease_term"], 100)
        adv   = trunc_str(row["advertentienummer"], 100)
        merk  = trunc_str(row["merk"], 100)
        model = trunc_str(row["model"], 100)
        transm= trunc_str(row["transmissie"], 50)
        prijs = trunc_str(row["prijs"], 50)
        brand = trunc_str(row["brandstof"], 50)
        btw   = trunc_str(row["btw_marge"], 50)
        addr  = trunc_str(row["address"], 200)
        # opties_accessoires is TEXT => no max
        opties= row["opties_accessoires"]

        listing_data = (
            url,
            title,
            subt,
            flp,
            flt,
            adv,
            merk,
            model,
            bouwjaar_str,
            kmstand_str,
            transm,
            prijs,
            brand,
            btw,
            opties,
            addr
        )

        try:
            print(f"\n[DEBUG] Inserting row {idx} into car_listings (no 'images' column).")
            cur.execute("""
                INSERT INTO car_listings (
                    url, title, subtitle, financial_lease_price, financial_lease_term,
                    advertentienummer, merk, model, bouwjaar, km_stand,
                    transmissie, prijs, brandstof, btw_marge, opties_accessoires,
                    address
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, listing_data)

            new_listing_id = cur.fetchone()[0]
            print(f"[DEBUG]  => Inserted new car_listings.id = {new_listing_id}")

            # Insert images in car_images
            raw_images = row["images"]
            if raw_images:
                urls = raw_images.split(",")
                for img_url in urls:
                    img_url = img_url.strip()
                    # Truncate each image URL to 500
                    img_url = trunc_str(img_url, 500)
                    if img_url:
                        print(f"     [DEBUG] Inserting image URL => {img_url}")
                        cur.execute("""
                            INSERT INTO car_images (image_url, car_listing_id)
                            VALUES (%s, %s);
                        """, (img_url, new_listing_id))

        except Exception as e:
            print(f"\n❌ Error on row {idx}: {e}")
            print("[DEBUG] Offending row data:\n", row)
            break  # Stop to see which row failed

    conn.commit()
    print("\n✅ Finished inserting rows into car_listings + car_images!")

except Exception as e:
    print("\n❌ Overall connection or query error:")
    print(e)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
    print("[DEBUG] Connection closed.")
