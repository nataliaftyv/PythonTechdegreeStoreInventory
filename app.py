from peewee import *
from collections import OrderedDict
import datetime
import csv
import sys


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


def load_to_db(file_name: str):
    """Takes cleaned csv file name and loads all rows into sqlite database,
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
                    if duplicate.date_updated <= new_item_date_obj:
                        duplicate.delete_instance()
                        Product.create(product_name=row['product_name'],
                                       product_price=row['product_price'],
                                       product_quantity=row['product_quantity'],
                                       date_updated=row['date_updated']
                                       )
                continue


def clean_data(initial_file_name: str, cleaned_file_name: str):
    """takes a csv file name and a desired target csv file name as strings
    writes cleaned data to the target file"""

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


def create_entry():
    """Add a new product to the database"""

    name = input('Product Name: ').capitalize()
    quantity = input('Product Quantity: ')
    price = input('Product Price: ')
    try:
        Product.create(product_name=name, product_quantity=quantity, product_price=price)
        print('Product added to the database!')
    except IntegrityError:
        duplicate = Product.get(Product.product_name == name)
        duplicate.product_quantity = quantity
        duplicate.product_price = price
        duplicate.date_updated = datetime.datetime.now()
        duplicate.save()
        print(f"Product information for {duplicate.product_name} is updated!")


def view_entry():
    """View a single product's inventory"""
    try:
        input_id: int = int(input('Enter product id: '))
        selected_product = Product.get_by_id(input_id)
        date_str = selected_product.date_updated.strftime('%b %d %Y %H:%M:%S')
        print(f'Product Name: {selected_product.product_name} '
              f'\nPrice: {selected_product.product_price} '
              f'\nQuantity: {selected_product.product_quantity} '
              f'\nDate Updated: {date_str}')

    except DoesNotExist:
        print('Oops! No entry with this id! Please enter a valid id!')
        view_entry()


def db_backup():
    """Make a backup of the entire inventory"""
    data = Product.select().dicts()
    with open('backup.csv', 'w') as backup_file:
        fieldnames = ['product_id', 'product_name', 'product_price', 'product_quantity', 'date_updated']
        writer = csv.DictWriter(backup_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print('Contents of the database are now in this file: backup.csv')


def delete_entry(key):
    entry = Product.get_by_id(key)
    entry.delete_instance()
    print('Deleted')


def display_menu():
    menu = OrderedDict(
        [
            ('v', view_entry),
            ('a', create_entry),
            ('b', db_backup),
        ]
    )

    user_input = None
    print('Press q for exit at any time')
    while user_input != 'q':
        print('Here are the options:')
        for key, option in menu.items():
            print(key, option.__doc__)

        user_input = input('Press corresponding letter for desired function: ').lower().strip()

        if user_input in menu:
            menu[user_input]()
        elif user_input == 'q':
            sys.exit()
        else:
            print('This is not a valid option! Please press a valid letter from the menu.')


if __name__ == '__main__':
    initialize_db()
    clean_data('inventory.csv', 'cleaned_inventory.csv')
    load_to_db('cleaned_inventory.csv')
    display_menu()
