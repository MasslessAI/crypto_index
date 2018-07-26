import os
import sys
sys.path.append('../')
sys.path.append('/home/cqtrun/dailyRun/env0/bin/crypto_index')
import cqt
import cqt.datagen as dg
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy import and_
import json

db_cfg_file = '%s/db.cfg' % (os.path.dirname(os.path.realpath(__file__)))


class IndexedDBObj(object):

    def __init__(self, df, id):
        # print(df)
        #self.data = df.rename(index=str, columns={'price_close':'close','price_open':'open','price_high':'high','price_low':'low'}, inplace=True)
        # print(self.data)
        self.data = df
        self.id = id
        tmp = id.split('-')
        self.source = tmp[0]
        self.type = tmp[1]
        self.symbol = tmp[2]
        self.period = tmp[3]
        self.setFromToDates()
        # self.data.rename(index=str, columns={
        #                  'price_close': 'close', 'price_open': 'open', 'price_high': 'high', 'price_low': 'low'}, inplace=True)

    def setFromToDates(self):
        self.fromTime = self.data.key.sort_values().iloc[0]
        self.toTime = self.data.key.sort_values().iloc[-1]

    def get_index_data(self):
        request_dict = dict()
        request_dict['request_type'] = self.type
        request_dict['period'] = self.period
        request_dict['symbol_id'] = self.symbol
        return dg.IndexedData(self.source, request_dict, self.data)


def error(msg):
    print(msg)
    sys.exit(64)


def db_connect(url):
    disk_engine = create_engine(url)
    conn = disk_engine.connect()
    return (conn, disk_engine)


def getUrlFromCfg(db_cfg_file, db_id):
    with open(db_cfg_file) as f:
        cfg_str = f.read()
        cfg_data_full = json.loads(cfg_str)
    cfg_data = cfg_data_full[db_id]
    url = '%s://%s:%s@%s:%s/%s' % (cfg_data['db_engine'], cfg_data['username'], cfg_data[
                                   'password'], cfg_data['hostname'], cfg_data['port'], cfg_data['db_name'])
    return url


def genAddPrimaryKeySQL(tbl, key_field):
    add_primary_key = 'alter table "%s" add primary key (%s)' % (
        tbl, key_field)
    return add_primary_key


def checkTableExistence(tbl, conn):
    sql_str = """SELECT to_regclass('public."%s"')""" % tbl
    sql_result = conn.execute(sql_str)
    for x in sql_result:
        if x[0] is None:
            return False
        else:
            return True


def mergeTwoTables(tbl_final, tbl_tmp, conn):
    column_names = "time_close, time_open, trades_count, price_low, price_open, price_close, key, volume_traded, price_high, last_updated"
    sql_str = 'insert into "%s" (%s)(select %s from "%s") on conflict (key) do nothing' % (
        tbl_final, column_names, column_names, tbl_tmp)
    print(sql_str)
    conn.execute(sql_str)
    return 0


def deleteTable(tbl, conn):
    sql_str = 'DROP TABLE IF EXISTS "%s"' % tbl
    conn.execute(sql_str)


def dump_to_db(df, tbl_name, key_field='key', db_id='Amazon_RDS'):

    url = getUrlFromCfg(db_cfg_file, db_id)
    (conn, engine) = db_connect(url)

    tbl_exists = checkTableExistence(tbl_name, conn)

    tbl_toDB = tbl_name
    if tbl_exists:
        tmp_tbl = 'tmp-' + tbl_name
        tbl_toDB = tmp_tbl

    now_str = str(datetime.now())
    df['last_updated'] = now_str

    df.to_sql(tbl_toDB, conn, if_exists='replace', index=False)
    add_primary_key = genAddPrimaryKeySQL(tbl_toDB, key_field)
    conn.execute(add_primary_key)

    if tbl_exists:
        mergeTwoTables(tbl_name, tmp_tbl, conn)
        deleteTable(tmp_tbl, conn)

    conn.close()


def get_table_list(db_id='Amazon_RDS'):
    url = getUrlFromCfg(db_cfg_file, db_id)
    (conn, engine) = db_connect(url)

    sql_str = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
    df = pd.read_sql(sql_str, conn)

    return df


def get_from_db(tbl_name, from_date='', to_date='', db_id='Amazon_RDS'):

    url = getUrlFromCfg(db_cfg_file, db_id)
    (conn, engine) = db_connect(url)

    tbl_exists = checkTableExistence(tbl_name, conn)

    if not tbl_exists:
        error('table %s does not exist!' % tbl_name)

    meta = MetaData(engine, reflect=True)
    table = meta.tables[tbl_name]

    if from_date == '' and to_date == '':  # select all
        select_str = select([table]).order_by(table.c.key)
    elif from_date == '':
        select_str = select([table]).where(table.c.key <= to_date).order_by(table.c.key)
    elif to_date == '':
        select_str = select([table]).where(table.c.key >= from_date).order_by(table.c.key)
    else:
        select_str = select([table]).where(
            and_(table.c.key >= from_date, table.c.key <= to_date)).order_by(table.c.key)

    df = pd.read_sql(select_str, conn)

    conn.close()

    DBObj = IndexedDBObj(df, tbl_name)

    return DBObj
