
import osgeo.gdal as gdal
import psycopg2
pgconn = psycopg2.connect(database='mesosite')
cursor = pgconn.cursor()

g = gdal.Open('a2m.png')

ct = g.GetRasterBand(1).GetColorTable()

db = 0
for i in range(ct.GetCount()):
    (r,g,b,a) = ct.GetColorEntry(i)
    if i == 255:
        db = None
    print db, i, r, g, b
    if max([r,g,b]) >= 256 or min([r,g,b]) < 0:
        print 'Invalid Color, assigning black!'
        r,g,b = [0,0,0]
    cursor.execute("""INSERT into iemrasters_lookup(
        iemraster_id, coloridx, value, r, g, b) VALUES (%s,%s,%s,%s,%s,%s)
        """, (3, i, db, r, g, b))
    if i == 255:
        break
    db += 0.1
    #if db > 95:
    #    break

cursor.close()
pgconn.commit()
pgconn.close()
    