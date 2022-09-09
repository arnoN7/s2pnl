from copy import copy

from app.home_receipt.models import *

def delete_orphan_shops():
    return None

def delete_receipt_and_paid_products(id_receipt):
    return None

def delete_alias(id_alias):
    return None

def delete_ophan_supplier():
    orphan_suppliers = db.session.query(Supplier).join(Bill, Bill.supplier_id == Supplier.id, isouter=True). \
        filter(Bill.id == None).all()
    for orphan in orphan_suppliers:
        Supplier.query.filter_by(id=orphan.id).delete()
        db.session.commit()

def get_suppliers():
    suppliers = Supplier.query.all()
    if suppliers is not None:
        return [(supplier.id, "{id}-{name}".format(id=supplier.id, name=supplier.name)) for supplier in suppliers]
    return None


def query2dicts(query):
    return [row2dict(row) for row in query]


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d
