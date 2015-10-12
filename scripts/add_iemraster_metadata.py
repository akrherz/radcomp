
import osgeo.gdal as gdal
import psycopg2
pgconn = psycopg2.connect(database='mesosite', host='localhost', port=5555,
                          user='mesonet')
cursor = pgconn.cursor()

feet = 0
for i, line in enumerate(open("../gempak/tables/luts/iem_eet.tbl")):
    if i == 0:
        continue
    if i == 72:
        break
    (r, g, b) = line.split()
    cursor.execute("""INSERT into iemrasters_lookup(
        iemraster_id, coloridx, value, r, g, b) VALUES (%s,%s,%s,%s,%s,%s)
        """, (9, i - 1, feet, r, g, b))
    feet += 1000

cursor.close()
pgconn.commit()
pgconn.close()
