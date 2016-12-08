from app import app
from app import bcrypt
from app import db
#from sqlalchemy import func

import datetime


class User(db.Model):
    """User represents a user account in the system
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    blocked = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, email="em@il", password="password", admin=False, blocked=True):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        )
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.blocked = blocked

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.String(1024), nullable=False)
    tjs_versions = db.Column(db.String(32), nullable=False)
    language = db.Column(db.String(32), nullable=False)
    activated = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<Service: {0}>".format(self.id)


class Framework(db.Model):
    """Framework represents a spatial framework in the OGC TJS terminology
    spatial framework
    a GIS representation, either point, line, or polygon, of any collection of physical or conceptual geographic
    objects. Municipalities, postal code areas, telephone area codes, ecoregions, watersheds, road segments, fire
    stations, and lighthouses are all examples of spatial frameworks.

    One framework may be associated with more than one service.
    One service may be associated with more than one framework
    """

    # TODO: make the framework - dataset relation a many to many one

    __tablename__ = "framework"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service = db.relationship('Service', backref=db.backref('frameworks', lazy='dynamic'))
    uri = db.Column(db.String(512))
    organization = db.Column(db.String(512))
    title = db.Column(db.String(512))
    abstract = db.Column(db.String(512))
    documentation = db.Column(db.String(512))
    version = db.Column(db.String(512))
    reference_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    key_col_name = db.Column(db.String(512))
    key_col_type = db.Column(db.String(512))
    key_col_length = db.Column(db.Integer)
    key_col_decimals = db.Column(db.Integer)
    bbox_south = db.Column(db.Numeric(8, 2))
    bbox_north = db.Column(db.Numeric(8, 2))
    bbox_west = db.Column(db.Numeric(8, 2))
    bbox_east = db.Column(db.Numeric(8, 2))

    def __init__(self, *args, **kwargs):
        super(Framework, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<Framework: {0}>".format(self.uri)


class DataSource(db.Model):
    """DataSource represents a database or file repository
    """
    __tablename__ = "data_source"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(512))
    type = db.Column(db.String(16))
    connect_string = db.Column(db.String(1024))

    def __init__(self, *args, **kwargs):
        super(DataSource, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<DataSource: id:{0} - title:{1}>".format(self.id, self.title)


class Dataset(db.Model):
    """Dataset represents a dataset in the OGC TJS terminology
    One dataset in associated with one and only one framework
    """
    __tablename__ = "dataset"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uri = db.Column(db.String(512))
    framework_id = db.Column(db.Integer, db.ForeignKey('framework.id'))
    framework = db.relationship('Framework', backref=db.backref('datasets', lazy='dynamic'))
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_source.id'))
    data_source = db.relationship('DataSource', backref=db.backref('datasets', lazy='dynamic', cascade="all,delete"))
    data_source_subset = db.Column(db.String(512))
    organization = db.Column(db.String(512))
    title = db.Column(db.String(512))
    abstract = db.Column(db.String(512))
    documentation = db.Column(db.String(512))
    version = db.Column(db.String(512))
    reference_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    activated = db.Column(db.Boolean, nullable=False, default=False)
    cached = db.Column(db.Boolean, nullable=False, default=False)
    cache_max_age = db.Column(db.Integer, nullable=False, default=86400)

    def __init__(self, *args, **kwargs):
        super(Dataset, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<Dataset: {0}>".format(self.uri)


class DatasetAttribute(db.Model):
    """DatasetAttribute represents an attribute of a dataset in the OGC TJS terminology
    One dataset attribute in associated with one and only one dataset
    """
    __tablename__ = "dataset_attribute"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataset_uri = db.Column(db.String(512), db.ForeignKey('dataset.uri'))
    dataset = db.relationship('Dataset', backref=db.backref('attributes', lazy='dynamic', cascade="all,delete"))
    purpose = db.Column(db.String(64))
    name = db.Column(db.String(512))
    type = db.Column(db.String(512))
    length = db.Column(db.Integer)
    decimals = db.Column(db.Integer)
    title = db.Column(db.String(512))
    abstract = db.Column(db.String(512))
    documentation = db.Column(db.String(512))
    values = db.Column(db.String(32))
    uom_short_form = db.Column(db.String(16))
    uom_long_form = db.Column(db.String(64))

    def __init__(self, *args, **kwargs):
        super(DatasetAttribute, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<DatasetAttribute: id:{0} - name:{1}>".format(self.id, self.name)
