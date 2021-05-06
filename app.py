from peewee import *
import datetime
import csv

# TODO: put back unique contraint for product name and re-load with conditions

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = PrimaryKeyField()
    product_name = CharField(max_length=255, unique=False)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def initialize_db():
    db.connect()
    db.create_tables([Product], safe=True)

def load_to_db(file_name):
    with open(file_name) as file:
        file_reader = csv.DictReader(file)
        rows = list(file_reader)
        for row in rows[1:]:
            Product.create(product_name=row['product_name'],
                           product_price=row['product_price'],
                           product_quantity=row['product_quantity'],
                           date_updated=row['date_updated']
                           )


def create_entry(productName, productQty, productPrice):
    Product.create(product_name=productName, product_quantity=productQty, product_price=productPrice)

def clean_data(initial_file_name, cleaned_file_name):
    #takes a csv file name and a desired target csv file name as strings,
    #writes cleaned data to the target file

    with open(initial_file_name, newline='') as initial_file:
        with open(cleaned_file_name, 'w') as cleaned_file:
            fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
            dict_writer = csv.DictWriter(cleaned_file, fieldnames=fieldnames)
            dict_writer.writeheader()
            inv_reader = csv.DictReader(initial_file)
            rows = list(inv_reader)
            for row in rows:
                row['date_updated'] = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y')
                price_list = list(row['product_price'])
                price_list.remove('$')
                price_list.remove('.')
                new_price_str = ''.join(price_list)
                new_price_cent = int(new_price_str)
                row['product_price'] = new_price_cent
                dict_writer.writerow(row)


#clean_data('inventory.csv', 'inventory_cleaned.csv')
initialize_db()
load_to_db('inventory_cleaned.csv')
# entries = Product.select()
# for entry in entries:
#     entry.delete_instance()











