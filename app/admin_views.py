# -*- coding: utf-8 -*-

from flask_login import current_user

from flask_admin.contrib.sqla import ModelView
from flask.ext.admin.form import rules

from app import db
from app import admin

from models.models import User
from models.models import Service
from models.models import DataSource
from models.models import Framework
from models.models import Dataset
from models.models import DatasetAttribute

# TODO: Add login and logout links in the admin pages templates

# TODO: use secure forms with Flask-Admin:
# http://flask-admin.readthedocs.io/en/latest/advanced/#enabling-csrf-protection

# TODO: create an admin view for symplifying the creation of datasets and datsetattribute records
# TODO: (just by selecting a datasource and a table)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class ServiceAdminView(AdminModelView):
    can_view_details = True
    column_list = (
        Service.title,
        Service.path,
        Service.activated
    )
    column_details_list = (
        Service.id,
        Service.path,
        Service.title,
        Service.abstract,
        Service.tjs_versions,
        Service.language,
        Service.activated
    )


class DataSourceAdminView(AdminModelView):
    can_view_details = True
    column_list = (
        DataSource.title,
        DataSource.type,
        DataSource.connect_string
    )
    column_details_list = (
        DataSource.id,
        DataSource.title,
        DataSource.type,
        DataSource.connect_string
    )
    column_filters = (DataSource.title, DataSource.type, DataSource.connect_string)
    form_choices = {
        "type": [
            ('db', u'Base relationnelle'),
            ('csv', u'Fichier CSV'),
            ('xls', u'Fichier Excel')
        ]
    }


# TODO: allow long text edition for abstract of Framework (multiple lines edit box)
class FrameworkAdminView(AdminModelView):
    can_view_details = True
    column_list = (
        Framework.title,
        Framework.organization,
        Framework.version,
        Framework.reference_date
    )
    column_details_list = (
        Framework.id,
        Framework.uri,
        Framework.title,
        Framework.abstract,
        Framework.documentation,
        Framework.version,
        Framework.organization,
        Framework.reference_date,
        Framework.start_date,
        Framework.key_col_name,
        Framework.key_col_type,
        Framework.key_col_length,
        Framework.key_col_decimals,
        Framework.bbox_south,
        Framework.bbox_north,
        Framework.bbox_east,
        Framework.bbox_west
    )
    form_choices = {
        "key_col_type": [
            ('https://www.w3.org/TR/xmlschema-2/#integer', u'Nombre entier'),
            ('https://www.w3.org/TR/xmlschema-2/#decimal', u'Nombre décimal'),
            ('https://www.w3.org/TR/xmlschema-2/#float', u'Nombre réel'),
            ('https://www.w3.org/TR/xmlschema-2/#string', u'Chaîne de caractères'),
            ('https://www.w3.org/TR/xmlschema-2/#boolean', u'Booléen')
        ]
    }
    column_filters = (Framework.title, Framework.abstract, Framework.organization)


# TODO: default organization for Dataset: the organization maintaining the server instance
# TODO: allow long text edition for abstract of Dataset (multiple lines edit box)
class DatasetAdminView(AdminModelView):
    can_view_details = True
    column_list = (
        Dataset.title,
        Dataset.organization,
        Dataset.version,
        Dataset.reference_date,
        Dataset.activated
    )
    column_details_list = (
        Dataset.id,
        Dataset.uri,
        Dataset.title,
        Dataset.abstract,
        Dataset.organization,
        Dataset.version,
        Dataset.reference_date,
        Dataset.start_date,
        'data_source.title',
        Dataset.data_source_subset,
        'framework.uri',
        'attributes',
        Dataset.activated,
        Dataset.cached,
        Dataset.cache_max_age,
        Dataset.documentation
    )
    column_filters = (Dataset.title, Dataset.abstract)


# TODO: allow long text edition for abstract of DatasetAttribute (multiple lines edit box)
class DatasetAttributeAdminView(AdminModelView):
    can_view_details = True
    column_list = (
        DatasetAttribute.id,
        DatasetAttribute.name,
        DatasetAttribute.title,
        DatasetAttribute.values
    )
    column_details_list = (
        DatasetAttribute.id,
        'dataset.uri',
        DatasetAttribute.name,
        DatasetAttribute.title,
        DatasetAttribute.abstract,
        DatasetAttribute.type,
        DatasetAttribute.length,
        DatasetAttribute.decimals,
        DatasetAttribute.purpose,
        DatasetAttribute.values,
        DatasetAttribute.uom_short_form,
        DatasetAttribute.uom_long_form,
        DatasetAttribute.documentation
    )
    form_choices = {
        "purpose": [
            ('Attribute', u'Attribute'),
            ('SpatialComponentIdentifier', u'SpatialComponentIdentifier'),
            ('SpatialComponentProportion', u'SpatialComponentProportion'),
            ('SpatialComponentPercentage', u'SpatialComponentPercentage'),
            ('TemporalIdentifier', u'TemporalIdentifier'),
            ('TemporalValue', u'TemporalValue'),
            ('VerticalIdentifier', u'VerticalIdentifier'),
            ('VerticalValue', u'VerticalValue'),
            ('OtherSpatialIdentifier', u'OtherSpatialIdentifier'),
            ('NonSpatialIdentifer', u'NonSpatialIdentifer')
        ],
        "values": [
            ('Count', u'Dénombrement'),
            ('Measure', u'Mesure'),
            ('Ordinal', u'Valeur ordinale'),
            ('Nominal', u'Valeur symbolique / nominale')
        ],
        "type": [
            ('https://www.w3.org/TR/xmlschema-2/#integer', u'Nombre entier'),
            ('https://www.w3.org/TR/xmlschema-2/#decimal', u'Nombre décimal'),
            ('https://www.w3.org/TR/xmlschema-2/#float', u'Nombre réel'),
            ('https://www.w3.org/TR/xmlschema-2/#string', u'Chaîne de caractères'),
            ('https://www.w3.org/TR/xmlschema-2/#boolean', u'Booléen')
        ]
    }
    column_filters = (DatasetAttribute.name,
                      DatasetAttribute.title,
                      DatasetAttribute.abstract,
                      DatasetAttribute.values)
    form_create_rules = [
        rules.FieldSet(("name", "title", "abstract"), u'Identification'),
        rules.FieldSet(("type", "length", "decimals", "purpose", "values"), u'Typologie'),
        rules.FieldSet(("uom_short_form", "uom_long_form"), u'Unité'),
        rules.FieldSet(("documentation",), u'Autres')
    ]

    # Use same rule set for edit page
    form_edit_rules = form_create_rules


admin.add_view(AdminModelView(User, db.session))
admin.add_view(ServiceAdminView(Service, db.session))
admin.add_view(DataSourceAdminView(DataSource, db.session))
admin.add_view(FrameworkAdminView(Framework, db.session))
admin.add_view(DatasetAdminView(Dataset, db.session))
admin.add_view(DatasetAttributeAdminView(DatasetAttribute, db.session))
