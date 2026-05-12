import mysql.connector


def get_connection(dbstring):

    host, u_ser, pass_wd, dbname, port = dbstring.split('#')

    db_connection = mysql.connector.connect(
        host=host,
        user=u_ser,
        passwd=pass_wd,
        database=dbname,
        port=int(port)
    )

    db_cursor = db_connection.cursor()

    return db_connection, db_cursor


def get_kv_llama_values(dbstring, doc_id):

    conn, curr = get_connection(dbstring)

    sql = """
    SELECT topic, topic_value
    FROM kvextract
    WHERE doc_id=%s
    """

    curr.execute(sql, (doc_id,))

    rows = curr.fetchall()

    data = {}

    for topic, value in rows:
        data[topic] = value or ""

    return data

def get_kv_bbox_details_annotated(doc_id, dbstring):

    conn, curr = get_connection(dbstring)

    sql = """
    select topic, topic_value
    from kv_extract_review
    where doc_id=%s
    """

    curr.execute(sql, (doc_id,))

    res = curr.fetchall()

    d = {}

    for tp, tpv in res:
        d[tp] = tpv

    return d