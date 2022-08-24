import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Project(Base):

    __tablename__ = 'project'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String(64))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    details = sa.Column(sa.Text())


class FilteredAddress(Base):

    __tablename__ = 'filtered_address'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    address = sa.Column(sa.String(64))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    details = sa.Column(sa.Text())


class Supplier(Base):

    __tablename__ = 'supplier'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String(64))
    address = sa.Column(sa.String(128))
    postcode = sa.Column(sa.Integer())
    city = sa.Column(sa.String(64))
    email = sa.Column(sa.String(64))
    siret = sa.Column(sa.String(32))
    phone = sa.Column(sa.String(256))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    details = sa.Column(sa.Text())


class Bill(Base):

    __tablename__ = 'bill'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    amount = sa.Column(sa.Float())
    date = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    dtn_end_amort = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    file = sa.Column(sa.String(256))
    details = sa.Column(sa.Text())
    supplier_id = sa.Column(sa.Integer(), sa.ForeignKey('supplier.id'))
    project_id = sa.Column(sa.Integer(), sa.ForeignKey('project.id'))
    cat_id = sa.Column(sa.Integer(), sa.ForeignKey('categorie.id'))


class Categorie(Base):

    __tablename__ = 'categorie'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String(64))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    details = sa.Column(sa.Text())


class Revenue(Base):

    __tablename__ = 'revenue'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    amount = sa.Column(sa.Float())
    client_id = sa.Column(sa.Integer(), sa.ForeignKey('client.id'))
    project_id = sa.Column(sa.Integer(), sa.ForeignKey('project.id'))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    details = sa.Column(sa.Text())


class Client(Base):

    __tablename__ = 'client'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String(128))
    address = sa.Column(sa.String(128))
    postcode = sa.Column(sa.Integer())
    city = sa.Column(sa.String(64))
    phone = sa.Column(sa.String(32))
    created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
    details = sa.Column(sa.Text())
