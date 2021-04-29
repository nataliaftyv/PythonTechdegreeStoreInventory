from peewee import *
import datetime
import csv

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = PrimaryKeyField()
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def initialize_db():
    db.connect()
    db.create_tables([Product], safe=True)


def create_entry(productName, productQty, productPrice):
    Product.create(product_name=productName, product_quantity=productQty, product_price=productPrice)

initialize_db()







