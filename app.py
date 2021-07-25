from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, CSRFProtect
from flask_table import Table, Col, LinkCol
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, InputRequired
from wtforms.fields.html5 import DateField
from methods import (Colleague,
                     LeaveRequest,
                     LeaveAllocation,
                     get_colleague_list,
                     get_leave_types,
                     get_leave_requests_table,
                     get_colleagues_table,
                     get_colleague
                     )

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
CSRFProtect(app)
app.config.update(
    DEBUG=True,
    WTF_CSRF_ENABLED=False,
    SECRET_KEY='you-will-never-guess'
)
# Flask-Bootstrap requires this line
Bootstrap(app)


def generate_page_list():
    pages = [
        {"name": "Home", "url": url_for("index")},
        {"name": "Colleagues", "url": url_for("colleagues")},
        {"name": "New Colleague", "url": url_for("new_colleague")},
        {"name": "Leave Requests", "url": url_for("leave_requests")},
        {"name": "New Leave Request", "url": url_for("new_leave_request")},
        {"name": "Set Leave Allocation", "url": url_for("new_allocation")}
    ]
    return pages


# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NewColleagueForm(FlaskForm):
    name = StringField('Colleague Name', validators=[DataRequired()])
    email = StringField('Colleague Email', validators=[DataRequired()])
    manager = SelectField('Manager', choices=None, validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditColleagueForm(FlaskForm):
    name = StringField('Colleague Name', validators=[DataRequired()])
    email = StringField('Colleague Email', validators=[DataRequired()])
    manager = SelectField('Manager', choices=None, validators=[DataRequired()], validate_choice=False)
    submit = SubmitField('Submit')


class NewAllocationForm(FlaskForm):
    colleague = SelectField('Colleague', choices=None, validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    allocation_days = IntegerField('Allocation Days', validators=[DataRequired()])
    submit = SubmitField('Submit')


class NewLeaveRequestForm(FlaskForm):
    colleague = SelectField('Colleague', choices=None, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    leave_type = SelectField('Leave Type', choices=None, validators=[DataRequired()])
    submit = SubmitField('Submit')


# Declare your table
class RequestsTable(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'no-wrap-centre']
    thead_classes = ['thead-purple']
    id = Col('Request ID')
    colleague_name = Col('Colleague Name')
    start_date = Col('Start Date')
    end_date = Col('End Date')
    leave_type_name = Col('Leave Type')
    status_name = Col('Request Status')

    def get_tr_attrs(self, leaverequesttableelement):
        if leaverequesttableelement.status_name == 'pending':
            return {'class': 'table-warning'}
        elif leaverequesttableelement.status_name == 'cancelled':
            return {'class': 'table-secondary'}
        elif leaverequesttableelement.status_name == 'approved':
            return {'class': 'table-success'}
        elif leaverequesttableelement.status_name == 'declined':
            return {'class': 'table-danger'}
        else:
            return {}


class ColleaguesTable(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'no-wrap-centre']
    thead_classes = ['thead-purple']
    id = Col('ID')
    name = Col('Name')
    email = Col('Email')
    manager_name = Col('Manager Name')
    edit = LinkCol('Edit', 'edit_colleague', url_kwargs=dict(id='id'))
    # button_attrs={'class': 'btn btn-warning btn-sm'}


# all Flask routes below
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', pages=generate_page_list())


@app.route('/colleagues/new', methods=['GET', 'POST'])
def new_colleague():

    form = NewColleagueForm()
    form.manager.choices = get_colleague_list()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        manager = form.manager.data

        coll = Colleague(name, email, manager)
        coll.create()
        flash("Created colleague successfully", "success")
        return redirect(url_for('colleagues'))
    return render_template('new_colleague.html', form=form, pages=generate_page_list())


@app.route('/colleagues/edit/<id>', methods=['GET', 'POST'])
def edit_colleague(id):
    colleagueinfo = get_colleague(id)
    form = EditColleagueForm(manager=colleagueinfo[0][2], name=colleagueinfo[0][0], email=colleagueinfo[0][1])
    managers = get_colleague_list()
    form.manager.choices = managers
    if form.validate_on_submit():
        form.manager.choices = managers
        name = form.name.data
        email = form.email.data
        manager = form.manager.data
        coll = Colleague(name, email, manager, id)
        coll.edit()

        flash("Edited colleague successfully", "success")
        return redirect(url_for('colleagues'))
    return render_template('edit_colleague.html', form=form, pages=generate_page_list())


@app.route('/allocation/new', methods=['GET', 'POST'])
def new_allocation():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NewAllocationForm()
    form.colleague.choices = get_colleague_list()
    message = ""
    if form.validate_on_submit():
        colleague = form.colleague.data
        year = form.year.data
        allocation_days = form.allocation_days.data

        allo = LeaveAllocation(colleague, year, allocation_days)
        allo.create()

        # empty the form field
        form.colleague.data = None
        form.year.data = None
        form.allocation_days.data = None

        flash("Created allocation successfully","success")
        return redirect(url_for('index'))
    return render_template('new_allocation_days.html', form=form, pages=generate_page_list())


@app.route('/leave_requests/new', methods=['GET', 'POST'])
def new_leave_request():
    form = NewLeaveRequestForm()
    form.leave_type.choices = get_leave_types()
    form.colleague.choices = get_colleague_list()

    if form.validate_on_submit():
        colleague = form.colleague.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        leave_type = form.leave_type.data

        req = LeaveRequest(colleague, start_date, end_date, leave_type)
        req.create()

        # empty the form field
        form.colleague.data = ""
        form.start_date.data = ""
        form.end_date.data = ""
        form.leave_type.data = ""

        flash("Created leave request successfully","success")
        return redirect(url_for('leave_requests', colleague_id=colleague))
    return render_template('new_leave_request.html', form=form, pages=generate_page_list())


@app.route('/leave_requests', methods=['GET', 'POST'])
def leave_requests():
    colleague_id = request.args.get('colleague_id', default=0, type=int)
    requests = get_leave_requests_table(colleague_id)
    table = RequestsTable(requests)
    # needs to be colleague id of the current user
    return render_template('leave_requests.html', table=table, pages=generate_page_list())


@app.route('/colleagues', methods=['GET', 'POST'])
def colleagues():
    colleagues = get_colleagues_table()
    table = ColleaguesTable(colleagues)
    return render_template('colleagues.html', table=table, pages=generate_page_list())

# 2 routes to handle errors - they have templates too

@app.errorhandler(404)
def page_not_found(e):
    flash("Page Not Found", "warning")
    return render_template('404.html', pages=generate_page_list()), 404

@app.errorhandler(500)
def internal_server_error(e):
    flash("Internal Server Error", "danger")
    return render_template('500.html', pages=generate_page_list()), 500


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)