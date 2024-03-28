"""Add metadata!"""

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute("DELETE from iemrasters_lookup where iemraster_id = 9")
    with open("../gempak/tables/luts/iem_eet.tbl", encoding="ascii") as fh:
        for i, line in enumerate(fh):
            if i == 72:  # EET
                break
            if i == 0:
                value = None
            else:
                value = 1 * (i - 1)  # EET
            (r, g, b) = line.strip().split()
            # 9 eet
            cursor.execute(
                "INSERT into iemrasters_lookup(iemraster_id, coloridx, value, "
                "r, g, b) VALUES (%s,%s,%s,%s,%s,%s)",
                (9, i, value, r, g, b),
            )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
