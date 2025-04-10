# image_new.py
import psycopg2

try:
    conn = psycopg2.connect("dbname=neolease_db host=localhost port=5432")
    cur = conn.cursor()

    # Step 1: read the car_listings with images from CSV column
    # We'll assume you inserted them into a column named "images" in car_listings
    cur.execute("SELECT id, images FROM car_listings WHERE images IS NOT NULL")

    rows = cur.fetchall()
    for row in rows:
        listing_id = row[0]
        image_csv  = row[1]  # e.g. "https://...,https://...,https://..."

        if not image_csv.strip():
            continue

        # Step 2: Split on commas
        image_urls = image_csv.split(",")

        # Step 3: For each URL, insert into car_images
        for url in image_urls:
            url = url.strip()
            if not url:
                continue

            print(f"Inserting image for listing {listing_id}: {url}")
            cur.execute("""
                INSERT INTO car_images (image_url, car_listing_id) 
                VALUES (%s, %s)
            """, (url, listing_id))

    conn.commit()

except Exception as e:
    print("❌ Error in image_new.py:", e)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()

print("✅ Done splitting images into car_images table.")
