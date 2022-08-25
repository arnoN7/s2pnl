# -*- encoding: utf-8 -*-
from datetime import datetime

import dateutil.utils
import os
from app.home_receipt import blueprint
from flask import render_template, request, redirect, url_for, json, session
from app.home_receipt.models import *
import app.home_receipt.constants as ct
from app.home_receipt.doc_read import parse_bill
from wtforms import Form, StringField, validators, FloatField, IntegerField, SelectField, DateField, FileField

from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
import app.home_receipt.breadcrumb as bc
import app.home_receipt.db_operations as op
from run import app


class AddProjectForm(Form):
    project_name = StringField('Product Name', [validators.DataRequired(), validators.Length(min=4, max=35)])

class AnalysisBillForm(Form):
    file_input = FileField("PDF file with bill details")
    supplier_select = StringField("Select Supplier", [validators.DataRequired()])

class AddBillForm(Form):
    supplier_select = StringField("Select Supplier", [validators.DataRequired()])
    vat_price = FloatField("VAT Price", [validators.DataRequired(), validators.number_range(min=0)])
    date = DateField("Bill date", [validators.DataRequired()])

class SettingsForm(Form):
    address = StringField("Address to exclude", [validators.DataRequired()])

@blueprint.app_template_filter('strftime')
def _jinja2_filter_datetime(date):
    return date.strftime("%d %B, %Y")


@blueprint.route('/')
def route_default():
    return redirect(url_for('receipt_blueprint.index'))

@blueprint.route('/index', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.', 'Home')
def index():
    query_pj = Project.query.all()
    bill_form = AddBillForm(request.form)
    file_form = AnalysisBillForm(request.form)
    return render_template('home-receipt/receipts_table.html', title='Bootstrap Table', projects=query_pj,
                           sel_project=get_sel_project(), form=bill_form, file_form=file_form)


@blueprint.route('/suppliers')
@register_breadcrumb(blueprint, '.suppliers', 'Suppliers')
def suppliers():
    query_pj = Project.query.all()
    query_suppliers = db.session.query(Supplier, func.count(Bill.id), func.sum(Bill.amount)).\
        join(Bill, Supplier.id == Bill.supplier_id). \
        filter(Bill.project_id == get_sel_project()).group_by(Supplier.id).all()
    return render_template('home-receipt/suppliers.html', title='Bootstrap Table', query=query_suppliers,
                           projects=query_pj, sel_project=get_sel_project())


@blueprint.route('/products')
@register_breadcrumb(blueprint, '.products', 'Products')
def products():
    return render_template('home-receipt/products_table.html', title='Bootstrap Table')


@blueprint.route('/receipt/<id_receipt>')
@register_breadcrumb(blueprint, '.receipt', '/', dynamic_list_constructor=bc.view_receipt_id)
def receipt_detail(id_receipt):
    return render_template('home-receipt/receipt_details_table.html', title='Bootstrap Table')


@blueprint.route('/project', methods=['GET', 'POST'])
def projects():
    query_pj = Project.query.all()
    form = AddProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        project = Project(name=form.project_name.data)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('receipt_blueprint.projects'))
    else:
        query = Project.query
        return render_template('home-receipt/projects_table.html', title='Bootstrap Table', form=form,
                           query=query.all(), year=dateutil.utils.today().year, projects=query_pj,
                           sel_project=get_sel_project())


@blueprint.route('/project/del/<id_project>')
def del_project(id_project):
    Project.query.filter_by(id=id_project).delete()
    db.session.commit()
    return redirect(url_for('receipt_blueprint.projects'))


@blueprint.route('/project/sel/<id_project>')
def select_project(id_project):
    session[ct.SEL_PROJECT] = int(id_project)
    return redirect(url_for('receipt_blueprint.index'))

@blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    query_pj = Project.query.all()
    form = SettingsForm(request.form)
    addresses = FilteredAddress.query.all()
    if request.method == 'POST' and form.validate():
        address = FilteredAddress(address=form.address.data)
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('receipt_blueprint.settings'))
    return render_template('home-receipt/settings.html', title='Bootstrap Table', form=form,
                           year=dateutil.utils.today().year, projects=query_pj,
                           sel_project=get_sel_project(), addresses=addresses)

@blueprint.route('/settings/del/<id_address>', methods=['GET'])
def del_settings(id_address):
    FilteredAddress.query.filter_by(id=id_address).delete()
    db.session.commit()
    return redirect(url_for('receipt_blueprint.settings'))


@blueprint.route('/bills', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.bills', 'Bills')
def bills():
    query_pj = Project.query.all()
    query_bill = db.session.query(Bill, Supplier).join(Supplier, Supplier.id == Bill.supplier_id).\
        filter(Bill.project_id == get_sel_project()).all()
    pj = Project.query.filter_by(id=get_sel_project()).first()
    if pj is None:
        app.logger.info("No project found can't add a Bill")
        return redirect(url_for('receipt_blueprint.index'))
    form = AnalysisBillForm(request.form)
    if request.method == 'POST':
        pf_folder = ct.PJ_FOLDER.format(id=pj.id, name=pj.name)
        if not os.path.exists(pf_folder):
            os.makedirs(pf_folder)
        uploaded_file = request.files[form.file_input.name]
        uploaded_file.save(pf_folder + uploaded_file.filename)
        parse_bill(pf_folder + uploaded_file.filename, pj.id)
        return redirect(url_for('receipt_blueprint.bills'))
    return render_template('home-receipt/add_bill.html', title='Bootstrap Table', form=form,
                           year=dateutil.utils.today().year, projects=query_pj, bills=query_bill,
                           sel_project=get_sel_project())


@blueprint.route('/bill/<id_bill>', methods=['GET', 'POST'])
def bill_details():

    return render_template('home-receipt/add_bill.html', title='Bootstrap Table', form=form,
                           year=dateutil.utils.today().year, projects=query_pj, bills=query_bill,
                           sel_project=get_sel_project())


@blueprint.route('/receipt/del/<id_receipt>')
def receipt_delete(id_receipt):
    op.delete_receipt_and_paid_products(id_receipt)
    op.delete_orphan_shops()
    return redirect(url_for('receipt_blueprint.index'))


def get_sel_project():
    if ct.SEL_PROJECT in session and session[ct.SEL_PROJECT] is not None:
        sel_pj = Project.query.filter_by(id=session[ct.SEL_PROJECT]).first()
        if sel_pj is None:
            # Selected project deleted
            app.logger.info('Selected project deleted id={id}'.format(id=session[ct.SEL_PROJECT]))
            session[ct.SEL_PROJECT] = None
    else:
        sel_pj = Project.query.first()
        if sel_pj is None:
            session[ct.SEL_PROJECT] = None
        else:
            session[ct.SEL_PROJECT] = sel_pj.id
    return session[ct.SEL_PROJECT]
