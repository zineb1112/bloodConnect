
import pandas as pd
import psycopg2
import os

#H: getting the fullfiled requests or the hospital's specific region 
def load_city_data(city, region):
    # Construct DATABASE_URL from environment variables or use provided DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Build connection string from individual environment variables
        db_host = os.getenv("DB_HOST", "db")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "blood_db")
        db_user = os.getenv("DB_USER", "blood_user")
        db_password = os.getenv("DB_PASSWORD", "blood_pass")
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    conn = psycopg2.connect(database_url)

    query = """
        SELECT 
            br.request_date,
            br.blood_type,
            br.quantity_needed,
            h.city,
            h.region
        FROM hospital_schema.hospital_app_bloodrequest br
        JOIN hospital_schema.hospital_app_hospital h ON br.hospital_id = h.id
        WHERE br.status = 'fulfilled'
          AND h.city = %s
          AND h.region = %s
        ORDER BY br.request_date;
    """

    df = pd.read_sql(query, conn, params=(city, region))
    conn.close()

    return df
