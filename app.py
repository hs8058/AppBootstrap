from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import boto3
from boto3.dynamodb.conditions import Key
from auth.oidc import oidc_login, oidc_callback, check_auth, oidc_logout
import uuid
from pynamodb.models import Model
from datetime import datetime,timezone
from dateutil import parser
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute



app = Flask(__name__)
app.secret_key = 'your-secret-key'




# Define a table as a Python class
class Offering(Model):
    class Meta:
        table_name = 'test_python_dashboard_table'
        region = 'us-east-1'
    ServiceProviderID = UnicodeAttribute(hash_key=True) #partition key
    SortKey = UnicodeAttribute(range_key=True)  # Sort key follows this format to be able to save multiple entities in the same table:  type#Offering#OfferingID#{offering_id_value}
    Title = UnicodeAttribute()
    Description = UnicodeAttribute()
    CreationMoment= UTCDateTimeAttribute()  # DateTime field
    Price = NumberAttribute()
    PublicationMoment= UTCDateTimeAttribute()  # DateTime field

#order 
class Order(Model):
    class Meta:
        table_name = 'test_python_dashboard_table'
        region = 'us-east-1'
    ServiceProviderID = UnicodeAttribute(hash_key=True) #partition key
    SortKey = UnicodeAttribute(range_key=True)  # Sort key follows this format to be able to save multiple entities in the same table:  type#Order#OrderID#{order_id_value}
    CreationMoment= UTCDateTimeAttribute()  # DateTime field
    Price = NumberAttribute()
    AmountPaid = NumberAttribute()
    BuyersEmailAddress=UnicodeAttribute()
    BuyersName=UnicodeAttribute()


# Routes for public pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Routes for authenticated pages
@app.route('/profile')
@check_auth  # Custom decorator to check if authenticated
def profile():
    return render_template('profile.html')

@app.route('/preferences')
@check_auth
def preferences():
    return render_template('preferences.html')

@app.route('/add_service')
@check_auth
def add_service():
    return render_template('add_service.html')

# OIDC Auth routes
@app.route('/login')
def login():
    return oidc_login()

@app.route('/login/callback')
def callback():
    return oidc_callback()


# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return oidc_logout()  # Redirect to oic provider's logout address 

@app.route('/postlogout')
def postlogout():
    
     return render_template('postlogout.html')



# Read data from DynamoDB table
@app.route('/read-data')
@check_auth
def read_data():
    try:
        # Scan the table (you can also query by keys)
        currentLoggedInOfferingProviderSUB=session.get('user')['sub']
        
        items = Offering.query(currentLoggedInOfferingProviderSUB , #partition key should be the identifier of the logged in user
                               Offering.SortKey.startswith(f'type#Offering#OfferingID#')  # list all rows whose sortkey starts with the pharse type#Offering#OfferingID#
        )
        return render_template('read_data.html', items=items)
    except Exception as e:
        return jsonify({'error': str(e)})
    
    
# Read data from DynamoDB table
@app.route('/read-orders')
@check_auth
def read_orders():
    try:
        # Scan the table (you can also query by keys)
        currentLoggedInOfferingProviderSUB=session.get('user')['sub']
        
        items = Order.query(currentLoggedInOfferingProviderSUB , #partition key should be the identifier of the logged in user
                               Order.SortKey.startswith(f'type#Order#OrderID#')  # list all rows whose sortkey starts with the pharse type#Offering#OfferingID#
        )
        return render_template('read_orders.html', items=items)
    except Exception as e:
        return jsonify({'error': str(e)})    

# Save data to DynamoDB table
@app.route('/save-data', methods=['GET', 'POST'])
@check_auth
def save_data():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        publicationMoment = parser.parse(request.form['publicationMoment'])
        price= float(request.form['price'])
        offering_id = str(uuid.uuid4())  # Generate a unique ID for the user
        creationMoment = datetime.now(timezone.utc)
        
        currentLoggedInOfferingProviderSUB=session.get('user')['sub']



        # Save data to DynamoDB
        try:
            
            # Creating a new event with the current time
            newOffering = Offering()
            newOffering.ServiceProviderID = currentLoggedInOfferingProviderSUB #partition key
            newOffering.SortKey = f'type#Offering#OfferingID#{offering_id}'  # Sort key
            newOffering.Title = title
            newOffering.Description = description
            newOffering.CreationMoment= creationMoment  # DateTime field
            newOffering.Price = price
            newOffering.PublicationMoment= publicationMoment # DateTime field        
            

            newOffering.save()

            return redirect(url_for('read_data'))
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('save_data.html')



if __name__ == '__main__':
    app.run(debug=True)
