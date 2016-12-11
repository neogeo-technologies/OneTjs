#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from app import app
from app import db
from app.models import User
from app.models import Framework
from app.models import Dataset
from app.models import DataSource
from app.models import Service
from app.models import DatasetAttribute

import os
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    logging.info(u"Creation of the database: {0}".format(db.app and db.app.config['SQLALCHEMY_DATABASE_URI'] or None))
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(email='ad@min.com', password='admin', admin=True, blocked=False))
    db.session.commit()


@manager.command
def create_data():
    """Creates sample data."""

    # Add a datasource record
    db_dir_path = os.path.split(os.path.realpath(__file__))[0]
    demo_db_path = os.path.join(db_dir_path, 'demo_data.sqlite')
    ds = DataSource(
        title="Demo database",
        type="db",
        connect_string="sqlite:///{}".format(demo_db_path)
    )

    s = Service(
        path=u"tjs",
        title=u"Prototype de service TJS",
        abstract=u"Service TJS développé par Neogeo Technologies",
        tjs_versions=u"1.0.0",
        language=u"fr-FR",
        activated=True
    )

    # Add a framework record
    f = Framework(
        service=s,
        uri="http://www.regionhautsdefrance.fr/data/geostats/frameworks/code-commune",
        organization=u"Région Hauts-de-France",
        title=u"Code commune",
        abstract=u"Découpage territorial à la commune. L'identifiant utilisé est le code INSEE de la commune.",
        version=u"",
        reference_date=datetime(2016, 1, 1),
        start_date=datetime(2016, 1, 1),
        key_col_name=u"code",
        key_col_type=u"https://www.w3.org/TR/xmlschema-2/#string",
        key_col_length=5,
        key_col_decimals=0,
        bbox_south=48.83,
        bbox_north=51.09,
        bbox_west=1.38,
        bbox_east=4.25
    )

    # Add a dataset record
    d1 = Dataset(
        uri="http://www.regionhautsdefrance.fr/data/geostats/datasets/demandeurs_emploi/hommes/2011",
        framework=f,
        data_source=ds,
        data_source_subset=u"demandeurs_emploi_hommes_2011",
        organization=u"Région Hauts-de-France",
        title=u"Nombre de demandeurs d'emploi dans les Hauts-de-Frances chez les hommes en 2011",
        abstract=u"Nombre de demandeurs d'emploi dans les Hauts-de-Frances chez les hommes en 2011.",
        version=u"1",
        reference_date=datetime(2011, 1, 1),
        start_date=datetime(2011, 1, 1),
        activated=True,
        cached=False
    )

    # Add a dataset record
    d2 = Dataset(
        uri="http://www.regionhautsdefrance.fr/data/geostats/datasets/familles_monoparentales/2012",
        framework=f,
        data_source=ds,
        data_source_subset=u"familles_monoparentales_2012",
        organization=u"Région Hauts-de-France",
        title=u"Part des familles monoparentales dans les Hauts-de-Frances en 2012",
        abstract=u"Part des familles monoparentales dans les Hauts-de-Frances en 2012.",
        version=u"1",
        reference_date=datetime(2012, 1, 1),
        start_date=datetime(2012, 1, 1),
        activated=True,
        cached=False
    )

    # TODO: Add csv datasets and attributes
    # TODO: Add Excel datasets and attributes

    # Add an attribute record
    da1 = DatasetAttribute(
        dataset=d1,
        purpose=u"Attribute",
        name="demandeurs_emplois_homme",
        type=u"https://www.w3.org/TR/xmlschema-2/#integer",
        length=8,
        decimals=0,
        title=u"Nombre de demandeurs d'emploi dans les Hauts-de-France chez les hommes en 2011",
        abstract=u"Nombre de demandeurs d'emploi dans les Hauts-de-France chez les hommes en 2011.",
        values=u"Count",
        uom_short_form=u"personnes",
        uom_long_form=u"personnes"
    )

    # Add an attribute record
    da2 = DatasetAttribute(
        dataset=d2,
        purpose=u"Attribute",
        name="part_des_menages",
        type=u"https://www.w3.org/TR/xmlschema-2/#decimal",
        length=8,
        decimals=2,
        title=u"Part des familles monoparentales dans les Hauts-de-Frances en 2012",
        abstract=u"Part des familles monoparentales dans les Hauts-de-Frances en 2012.",
        values=u"Measure",
        uom_short_form=u"%",
        uom_long_form=u"pourcentage"
    )

    db.session.add(ds)
    db.session.add(s)
    db.session.add(f)
    db.session.add(d1)
    db.session.add(d2)
    db.session.add(da1)
    db.session.add(da2)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
