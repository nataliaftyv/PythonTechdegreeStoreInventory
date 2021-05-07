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


def load_to_db(file_name):
    """Takes cleaved csv file and loads all rows into sqlite database,
        replaces duplicates with the most recently updated item
    """
    with open(file_name) as file:
        file_reader = csv.DictReader(file)
        rows = list(file_reader)
        for row in rows[1:]:
            try:
                Product.create(product_name=row['product_name'],
                               product_price=row['product_price'],
                               product_quantity=row['product_quantity'],
                               date_updated=row['date_updated']
                               )
            except IntegrityError:
                products = Product.select().order_by(Product.date_updated)
                duplicates = products.where(Product.product_name == row['product_name'])
                for duplicate in duplicates:
                    new_item_date_obj = datetime.datetime.strptime(row['date_updated'], '%Y-%m-%d %H:%M:%S')
                    if duplicate.date_updated < new_item_date_obj:
                        duplicate.delete_instance()
                        Product.create(product_name=row['product_name'],
                                       product_price=row['product_price'],
                                       product_quantity=row['product_quantity'],
                                       date_updated=row['date_updated']
                                       )
                continue




def create_entry(productName, productQty, productPrice):
    Product.create(product_name=productName, product_quantity=productQty, product_price=productPrice)
    # TODO: fix

def clean_data(initial_file_name, cleaned_file_name):
    # takes a csv file name and a desired target csv file name as strings
    # writes cleaned data to the target file

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


# clean_data('inventory.csv', 'inventory_cleaned.csv')
initialize_db()
load_to_db('inventory_cleaned.csv')
# entries = Product.select()
# for entry in entries:
#     entry.delete_instance()
