from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ItemForm, EmptyForm, DeleteForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Item
from werkzeug.urls import url_parse
from datetime import datetime
from decimal import Decimal

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index(): 
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, manufacturer=form.manufacturer.data,
                    purchase_date=form.purchase_date.data, purchase_price=form.purchase_price.data,
                    warranty = form.warranty.data, insured=form.insured.data,
                    current_value=form.current_value.data,serial=form.serial.data,
                    user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash('Item added to your inventory!')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    items = current_user.items.order_by(Item.timestamp.desc()).paginate(\
        page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('index', page=items.next_num) \
        if items.has_next else None
    prev_url = url_for('index', page=items.prev_num) \
        if items.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           items=items.items, next_url=next_url,
                           prev_url=prev_url)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') # Support for if a login_required page redirected to login, to send user back
        if not next_page or url_parse(next_page).netloc != '': # Avoids redirects by only accepting relative URLs
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, manufacturer=form.manufacturer.data,
                    purchase_date=form.purchase_date.data, purchase_price=form.purchase_price.data,
                    warranty = form.warranty.data, insured=form.insured.data,
                    current_value=form.current_value.data,serial=form.serial.data,
                    user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash('Item added to your inventory!')
        return redirect(url_for('index'))
    return render_template('add_item.html', title='Add Item',
                           form=form)

@app.route('/edit_item/<item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = db.session.query(Item).filter_by(id=item_id).first_or_404()
    form = ItemForm()
    confirmForm = DeleteForm()
    if form.delete.data:
        return render_template('edit_item.html', title='Edit Item',
                           form=form, confirmForm = confirmForm)
    if confirmForm.reallyDelete.data:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted!')
        return redirect(url_for('index'))
    elif form.validate_on_submit():
        item.name = str(form.name.data)
        item.manufacturer = form.manufacturer.data
        item.purchase_date = form.purchase_date.data
        item.purchase_price = form.purchase_price.data
        item.warranty = form.warranty.data
        item.insured = form.insured.data
        item.current_value = form.current_value.data
        item.serial = form.serial.data
        item.timestamp = datetime.utcnow()
        db.session.commit()
        flash('Item updated!')
        return redirect(url_for('index'))
    if item is not None:
        form.name.data = item.name
        form.manufacturer.data = item.manufacturer
        form.purchase_date.data = item.purchase_date
        form.purchase_price.data = item.purchase_price
        form.warranty.data = item.warranty
        form.insured.data = item.insured
        form.current_value.data = item.current_value
        form.serial.data = item.serial

    return render_template('edit_item.html', title='Edit Item',
                           form=form)