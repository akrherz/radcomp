import psycopg2

pgconn = psycopg2.connect(
    database="mesosite", host="localhost", port=5555, user="mesonet"
)
cursor = pgconn.cursor()

for i, line in enumerate(open("../gempak/tables/luts/iem_lut256.tbl")):
    if i == 0:
        value = None
    else:
        value = -32.5 + (0.5 * i)
    (r, g, b) = line.strip().split()
    cursor.execute(
        """INSERT into iemrasters_lookup(
        iemraster_id, coloridx, value, r, g, b) VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (2, i, value, r, g, b),
    )

cursor.close()
pgconn.commit()
pgconn.close()
