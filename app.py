from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate  # Import Migrate
from werkzeug.utils import secure_filename
import os
from forms import RequestForm, LoginForm, RegistrationForm
from models import db, User, Request
from config import Config
from datetime import datetime

# flask db init
# flask db migrate -m "Description of the changes"
# flask db upgrade



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

migrate = Migrate(app, db)  # Initialize Migrate

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(int(user_id))
    return db.session.get(User,int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('با موفقیت ثبت نام شدید', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('نام کاربری و یا پسورد اشتباه می باشد.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'client':
        requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.date_created.desc()).all()
    else:
        requests = Request.query.order_by(Request.date_created.desc()).all()  # Operators see all requests
    return render_template('dashboard.html', requests=requests)

@app.route('/request/new', methods=['GET', 'POST'])
@login_required
def new_request():
    form = RequestForm()
    if form.validate_on_submit():
        file = request.files['File']
        if file:
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename, os.path.join(app.config['UPLOAD_FOLDER']))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            print(f"Saving file to: {file_path}")

            file.save(file_path)
            new_request = Request(
                title=form.title.data,
                description=form.description.data,
                filename=unique_filename,  # Save the filename in the database
                user_id=current_user.id,
                status='منتظر تایید'
            )
            db.session.add(new_request)
            db.session.commit()
            flash('درخواست با موفقیت ثبت شد', 'success')
            return redirect(url_for('dashboard'))
        else:
            filename = ''
            new_request = Request(title=form.title.data, description=form.description.data, filename=filename, user_id=current_user.id, status='منتظر تایید')
            db.session.add(new_request)
            db.session.commit()
            flash('درخواست با موفقیت ثبت شد', 'success')
            return redirect(url_for('dashboard'))
    else:
        print(form.errors)

    return render_template('request_form.html', form=form)

@app.route('/request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    request_to_update = Request.query.get_or_404(request_id)
    request_to_update.status = 'در حال انجام'
    db.session.commit()
    flash('درخواست تایید شد و در وضعیت در حال انجام قرار گرفت', 'success')
    return redirect(url_for('dashboard'))

@app.route('/request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    request_to_update = Request.query.get_or_404(request_id)
    request_to_update.status = 'نیاز به بررسی دارد'
    db.session.commit()
    flash('درخواست رد شد، نیاز به بازبینی بیشتر دارد', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/request/<int:request_id>/done', methods=['POST'])
@login_required
def Done_request(request_id):
    request_to_update = Request.query.get_or_404(request_id)
    request_to_update.status = 'آماده تحویل'
    db.session.commit()
    flash('خداقوت، درخواست با موفقیت پایان یافت', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/request/edit/<int:request_id>', methods=['GET', 'POST'])
@login_required
def edit_request(request_id):
    request_to_edit = Request.query.get_or_404(request_id)
    if request_to_edit.user_id != current_user.id or request_to_edit.status != 'نیاز به بررسی دارد':
        flash('درخواست مورد نظر برای شما قابل ویرایش نیست', 'danger')
        return redirect(url_for('dashboard'))
    
    form = RequestForm(obj=request_to_edit)
    if form.validate_on_submit():
        request_to_edit.title = form.title.data
        request_to_edit.description = form.description.data
        request_to_edit.status = 'ویرایش شده'

        file = request.files['File']
        if file:
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename, os.path.join(app.config['UPLOAD_FOLDER']))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            print(f"Saving file to: {file_path}")
            file.save(file_path)

            request_to_edit.filename = unique_filename
            db.session.commit()
            flash('درخواست با موفقیت ثبت شد', 'success')
            return redirect(url_for('dashboard'))
        else:
            filename = form.filename.data

            db.session.commit()
            flash('درخواست با موفقیت ثبت شد', 'success')
            return redirect(url_for('dashboard'))

    else:
        print(form.errors)
    return render_template('request_form_edit.html', form=form)

## Edit_New
@app.route('/request/view/<int:request_id>')
@login_required
def view_request(request_id):
    request_to_view = Request.query.get_or_404(request_id)
    print(f"Request Data: {request_to_view}")
    return render_template('request_form_view.html', request=request_to_view)
##

@app.route('/uploads/<filename>')
@login_required
def download_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    print(f"Opening file : {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")

    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename, as_attachment=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def generate_unique_filename(filename, upload_folder):
    """
    Generate a unique filename by appending a timestamp.  if a file with the same name exists.
    """
    base_name, ext = os.path.splitext(filename)  # Split filename and extension
    counter = 1
    new_filename = filename

    # Check if the file already exists
    while os.path.exists(os.path.join(upload_folder, new_filename)):
        # Append a timestamp or counter to the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{base_name}_{timestamp}{ext}"
        counter += 1

    return new_filename



migrate = Migrate(app, db)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()  # Create database tables
#    app.run(debug=True, port=5000)
    app.run(debug=True, host="0.0.0.0", port=8080)

