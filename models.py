# models.py
from datetime import date
from flask_sqlalchemy import SQLAlchemy

# Ініціалізація SQLAlchemy
db = SQLAlchemy()


class StorageUnit(db.Model):
    __tablename__ = 'storage_units'

    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    car_number = db.Column(db.String(50), nullable=True)
    car_model = db.Column(db.String(50), nullable=True)
    tire_width = db.Column(db.String(10), nullable=False, default='')
    tire_profile = db.Column(db.String(10), nullable=False, default='')
    tire_diameter = db.Column(db.String(10), nullable=False, default='')
    tire_name = db.Column(db.String(100), nullable=True)
    has_disks = db.Column(db.Boolean, nullable=False, default=False)
    tire_quantity = db.Column(db.Integer, nullable=False)
    storage_date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))  # ID склада
    warehouse = db.relationship('Warehouse', back_populates='storage_units',)  # Обратная связь
    row = db.Column(db.String(100), nullable=True, default='')
    place = db.Column(db.String(100), nullable=True, default='')  # Новое поле для Місце

    def __init__(self, unit_id, full_name, phone, car_number, car_model, tire_width, tire_profile, tire_diameter,
                 tire_name, has_disks, tire_quantity, storage_date, warehouse_id, warehouse, place, row):
        self.unit_id = unit_id
        self.full_name = full_name
        self.phone = phone
        self.car_number = car_number
        self.car_model = car_model
        self.tire_width = tire_width
        self.tire_profile = tire_profile
        self.tire_diameter = tire_diameter
        self.tire_name = tire_name
        self.has_disks = has_disks
        self.tire_quantity = tire_quantity
        self.storage_date = storage_date
        self.warehouse = warehouse
        self.warehouse_id = warehouse_id
        self.row = row
        self.place = place


class Warehouse(db.Model):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rows = db.Column(db.Integer, nullable=False, default=10)  # Количество рядов
    columns = db.Column(db.Integer, nullable=False, default=10)  # Количество мест в ряду
    layout = db.Column(db.JSON, nullable=False)  # Хранит пользовательскую конфигурацию

    def __init__(self, name, rows, columns, layout=None):
        self.name = name
        self.rows = rows
        self.columns = columns
        self.layout = layout
    storage_units = db.relationship('StorageUnit', back_populates='warehouse', cascade='all, delete-orphan')
