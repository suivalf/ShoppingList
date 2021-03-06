from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)
app.secret_key = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fhsgnjxnwwlekg:310ee1fe4f7cdd7b103d3f2d0424fb3d7b6da13f8568ea5b3c5c9e3cb7dd12de@ec2-54-217-235-87.eu-west-1.compute.amazonaws.com:5432/d4de83c852dcei'
db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(200), nullable=False)
    item_qty = db.Column(db.Integer, nullable=True)
    def __init__(self, item_name, item_qty):
        self.item_name = item_name
        self.item_qty = item_qty
    def __repr__(self):
        return '<Item: %r, Name: %r, Quantity: %r>' % self.id % self.item_name % self.item_qty

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        #Input validation
        if request.form['name'].strip() == '' and request.form['qty'] == '' or request.form['name'].strip() == '':
            flash("Oops. No item name provided!", "warning")
            return redirect('/')
        item_name = request.form['name'].strip()
        if request.form['qty'] == '': # If we don't specify a quantity, add a default quantity of 1
            item_qty = 1
        elif int(request.form['qty']) > 999999999:
            flash("Oops. Quantity too big!", "warning")
            return redirect('/')
        else:
            item_qty = int(request.form['qty'])
        # Check if we already have that item in our shopping list
        entries = Item.query.filter_by(item_name=item_name)
        if entries.count() == 0: # If we don't have that item, just add it.
            new_item = Item(item_name = item_name, item_qty = item_qty)
        else: #If we have that item, increase it's quantity
            new_item = Item.query.filter_by(item_name = item_name).first()
            new_item.item_qty += item_qty
        try:
            db.session.add(new_item)
            db.session.commit()
            flash("Added!", "warning")
            return redirect('/')
        except:
            return 'Error adding Item'
    else:
        shopping_list = Item.query.order_by(Item.id).all()
        return render_template('index.html', shopping_list = shopping_list)

@app.route('/delete/<int:id>')
def delete(id):
    item_to_delete = Item.query.get_or_404(id)
    
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that Item'


@app.route('/decrement/<int:id>', methods=['GET','POST'])
def decrement(id):
    item = Item.query.filter_by(id = id).first()
    item.item_qty -= 1
    if item.item_qty <= 0: # If quantity of an item reaches 0, delete it from the list
        delete(id)
        return redirect('/')
    try:
        db.session.add(item)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error Decrementing'

@app.route('/increment/<int:id>', methods=['GET','POST'])
def increment(id):
    item = Item.query.filter_by(id = id).first()
    item.item_qty += 1
    try:
        db.session.add(item)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error Incrementing'
    

if __name__ == "__main__":
    app.run(debug=True)

