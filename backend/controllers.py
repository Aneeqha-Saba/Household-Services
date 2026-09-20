from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import current_app as app 
from flask import send_from_directory
from .models import *
from decimal import Decimal
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date
from sqlalchemy import func, or_
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt


#front page
@app.route("/")
def home():
    return render_template("house_hold.html")

#custom IDs for customers
def generate_customer_id():
    last_cus = Customer.query.order_by(Customer.id.desc()).first()
    next_id = int(last_cus.id[1:]) + 1 if last_cus else 1
    return f"1{next_id:02}"

#customer signup
@app.route("/customer_register", methods=["GET", "POST"])
def cus_signup():
       if request.method == "POST":
              email = request.form.get("email")
              password = request.form.get("password")
              fullname = request.form.get("fullname")
              phone = request.form.get("phone")
              address = request.form.get("address")
              pincode = request.form.get("pincode")
              cus = Customer.query.filter_by(email=email).first()
              if not cus:
                     new_cus = Customer(
                            id=generate_customer_id(),
                            email=email,
                            password=password,
                            fullname=fullname,
                            phone=phone,
                            address=address,
                            pincode=pincode
                            )
                     db.session.add(new_cus)
                     db.session.commit()
                     return render_template("login.html", msg="Registered successfully!!")
              else:
                     return render_template("customer_register.html", msg="Email already exists!!")
       return render_template("customer_register.html")

#professional CV
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#custom IDs for professionals
def generate_professional_id():
    last_pro = Professional.query.order_by(Professional.id.desc()).first()
    next_id = int(last_pro.id[1:]) + 1 if last_pro else 1
    return f"0{next_id:02}" 

#professional signup
@app.route("/professional_register", methods=["GET", "POST"])
def pro_signup():
    services = Service.query.all()    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        service_name = request.form["service_name"]
        specification = request.form.get("specification")
        phone = request.form.get("phone")
        experience = request.form.get("experience")
        documents = request.files["documents"]
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        pro = Professional.query.filter_by(email=email).first()
        if not pro:
            if documents and allowed_file(documents.filename):
                new_pro_id = generate_professional_id()
                filename = secure_filename(documents.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                documents.save(file_path)

                new_pro = Professional(
                    id=new_pro_id,  
                    email=email,
                    password=password,
                    fullname=fullname,
                    service_name=service_name,
                    specification=specification,
                    phone=phone,
                    experience=experience,
                    documents=filename,
                    address=address,
                    pincode=pincode,
                    status="Pending",
                    is_approved=False,
                )
                db.session.add(new_pro)
                db.session.commit()
                return render_template("login.html", msg="Registered successfully!!")
            else:
                return render_template("professional_register.html", msg="Invalid file format. Only PDF allowed.", services=services)
        else:
            return render_template("professional_register.html", msg="Email already exists!!", services=services)
    return render_template("professional_register.html", services=services)

#login
@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("password")
        
        admin = Admin.query.filter_by(email=uname, password=password).first()
        cus = Customer.query.filter_by(email=uname, password=password).first()
        pro = Professional.query.filter_by(email=uname, password=password).first()
        
        if admin:
            unapproved_professionals = Professional.query.filter_by(is_approved=False).all()
            return redirect(url_for("admin_home",
                                    professionals=unapproved_professionals,
                                    name=admin.email))
        
        elif cus:
            if cus.is_blocked:
                return render_template("blocked.html", msg="Your account has been blocked.")
            service = Service.query.all()
            session['customer_id'] = cus.id
            session['customer_name'] = cus.fullname
            return redirect(url_for('customer_home', name=cus.fullname, services=service))
        
        elif pro:
            if pro.is_blocked:
                return render_template("blocked.html", msg="Your account has been blocked.")
            
            if pro.is_approved:
                session['pro_id'] = pro.id
                session['pro_name'] = pro.fullname
                return redirect(url_for("professional_home", name=pro.fullname))
            else:
                return render_template("login.html", msg="Your account is not approved yet.")
        
        else:
            return render_template("login.html", msg="Invalid credentials!")
    
    return render_template("login.html", msg="")

#dictionary to store all the services, prevent duplicate entries
services = {}
def get_all_services():
    services.clear()  
    services_from_db = Service.query.all()  
    for service in services_from_db:
        services[service.id] = [service.name, service.description, service.price, service.time_required]
    return services

#based on the id displays the service details
def service_id(id):
    l = get_all_services()
    return l.get(id)
          
#update the average rating of a professional
def update_professional_average_rating(professional_id):
    average_rating = db.session.query(
        func.avg(ServiceRequest.rating)
    ).filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.rating.isnot(None)
    ).scalar()
    professional = Professional.query.get(professional_id)
    if professional:
        professional.avg_rating = round(average_rating, 2) if average_rating else None
        db.session.commit()

#admin home CHATGPT CHECK CODE SERVICES 
@app.route("/admin/home", methods=["GET", "POST"])
def admin_home():
    admin = Admin.query.filter_by(id=1).first()
    if not admin:
        return "Admin with id=1 not found.", 404  # Return an error if no admin found
    
    unapproved_professionals = Professional.query.filter_by(is_approved=False).all()
    service = service_id(id)
    requested_data = ServiceRequest.query.all()
    
    return render_template(
        "admin_home.html",
        name=admin.email,
        service=service,
        services=services,
        professionals=unapproved_professionals,
        requested_data=requested_data
    )

#Custom service id
def generate_service_id():
    last_service = Service.query.order_by(Service.id.desc()).first()
    next_id = int(last_service.id[2:]) + 1 if last_service else 1
    return f"00{next_id:03}"  # Format as 001, 002, 003, etc.

#create service
@app.route('/admin/service', methods=["GET",'POST'])
def create_service():
    try:
        ser_name = request.form['ser_name']
        description = request.form['description']
        price = Decimal(request.form['price'])
        time_required = request.form['time_required'] 

        new_service = Service(
            id=generate_service_id(),  # Explicitly setting custom ID here
            name=ser_name, 
            description=description, 
            price=price, 
            time_required=time_required
        )
        db.session.add(new_service)
        db.session.commit()
        return redirect('/admin/home?msg=Service+created+successfully')
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")
        return redirect('/admin/home?msg=Error+creating+service')

#editing the created service
@app.route("/admin/service/edit/<service_id>", methods=["GET", "POST"])
def edit_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    if request.method == "POST":
        service.name = request.form['ser_name']
        service.description = request.form['description']
        service.price = Decimal(request.form['price'])
        service.time_required = request.form['time_required']
        db.session.commit()
        return redirect('/admin/home?msg=Service+updated+successfully')
    return render_template("admin_home.html", service=service)
   
#deleting the created service
@app.route("/admin/service/delete/<service_id>", methods=["GET", "POST"])
def delete_service(service_id):
      if request.method == "POST":
            service = Service.query.filter_by(id=service_id).first()
            if service:
                professional = Professional.query.filter_by(service_name=service.name).all()
                for pro in professional:
                     db.session.delete(pro)
            db.session.delete(service)
            db.session.commit()
            return redirect('/admin/home?msg=Service+and+associated+professinals+deleted+successfully')
      return render_template("admin_home.html")

#approving a professional
@app.route("/admin/professional/accept/<string:professional_id>", methods=["GET", "POST"])
def accept_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.is_approved = True
    db.session.commit()
    return redirect('/admin/home?msg=Professional+accepted+successfully')

#rejecting a professional
@app.route("/admin/professional/reject/<string:professional_id>", methods=["GET","POST"])
def reject_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.is_approved = False
    db.session.commit()
    return redirect('/admin/home?msg=Professional+rejected+successfully')

#deleting a professional
@app.route("/admin/professional/delete/<string:professional_id>", methods=["GET","POST"])
def delete_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    db.session.delete(professional)
    db.session.commit()
    return redirect('/admin/home?msg=Professional+deleted+successfully')

#viewing professional's details
@app.route("/admin/professionals")
def view_professionals():
    pro = Professional.query.all()
    ser = pro.service_name
    return render_template("admin_professionals.html", pro=pro, ser=ser)

#view the cv uploads for professionals
@app.route('/admin/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#search for customers and professionals
@app.route("/admin/search", methods=["GET", "POST"])
def admin_search():
    admin = Admin.query.filter_by(id=1).first()
    q = request.form.get('t_search', '').strip()
    searchby_ = request.form.get('searchby_')
    search_results = []
    if searchby_ == "cust":
        search_results = ServiceRequest.query.join(Customer).filter(Customer.fullname.ilike(f"%{q}%")).all()
    elif searchby_ == "prof":
        search_results = Professional.query.filter(Professional.is_approved == True, Professional.fullname.ilike(f"%{q}%")).all()


    blocked_customers = Customer.query.filter_by(is_blocked=True).all()
    blocked_professionals = Professional.query.filter_by(is_blocked=True).all()


    return render_template(
        "admin_search.html",
        name=admin.email,
        search_results=search_results,
        searchby_=searchby_,
        blocked_customers=blocked_customers,
        blocked_professionals=blocked_professionals
    )

#blocking a user
@app.route("/admin/block/<string:user_id>", methods=["POST"])
def block_user(user_id):
    user = db.session.query(Customer).get(user_id) or db.session.query(Professional).get(user_id)
    if user:
        user.is_blocked = True
        db.session.commit()
    return redirect(url_for('admin_search')) 

#unblocking a user
@app.route("/admin/unblock/<string:user_id>", methods=["POST"])
def unblock_user(user_id):
    user = db.session.query(Customer).get(user_id) or db.session.query(Professional).get(user_id)
    if user:
        user.is_blocked = False
        db.session.commit()
    return redirect(url_for('admin_search')) 

#summary displaying the number of requests
@app.route("/admin/summary/", methods=["GET", "POST"])
def admin_summary():
    admin = Admin.query.filter_by(id=1).first()
    if not admin:
        return "Admin with id=1 not found.", 404

    req_counts = {
        "Closed": 0,
        "Rejected": 0,
        "Requested": 0,
        "Accepted": 0
    }
    for req in ServiceRequest.query.all():
        req_counts[req.status] += 1
    
    req_labels = ["Closed", "Rejected", "Requested", "Accepted"]
    req_values = [req_counts["Closed"], req_counts["Rejected"], req_counts["Requested"], req_counts["Accepted"]]
    bar_chart_path = 'static/img/summaries/admin_summary_bar.png'

    plt.bar(req_labels, req_values, color=['lightgreen', 'salmon', 'skyblue', 'lightcoral'])
    plt.savefig(bar_chart_path)
    plt.clf()

    return render_template(
        "admin_summary.html",
        name=admin.email,
        bar_chart_path=bar_chart_path,
    )

#customer home
@app.route("/customer/home", methods=["GET"])
def customer_home():
    customer_id = session.get('customer_id')
    if not customer_id:
        return redirect(url_for('user_login'))
    
    customer = Customer.query.get(customer_id)

    services = Service.query.all()
    services_with_professionals = []

    for service in services:
        professionals = Professional.query.filter_by(service_name=service.name, is_approved=True, is_blocked=False).all()
        services_with_professionals.append({
            "service": service,
            "professionals": professionals
        })

    service_history = ServiceRequest.query.filter_by(customer_id=customer_id).all()

    return render_template(
        "cust_home.html",
        services_with_professionals=services_with_professionals,
        service_history=service_history,
        name=customer.fullname,
        customer=customer
    )

#customer profile
@app.route("/customer/update_profile", methods=["POST"])
def update_cus_profile():
    customer_id = session.get('customer_id')
    if not customer_id:
        return redirect(url_for('user_login'))

    customer = Customer.query.get(customer_id)
    if customer:
        customer.fullname = request.form.get("fullname")
        customer.password = request.form.get("password")  # Hash if necessary
        customer.phone = request.form.get("phone")
        customer.address = request.form.get("address")
        customer.pincode = request.form.get("pincode")

        db.session.commit()
        flash("Profile updated successfully", "success")
    else:
        flash("Customer not found", "error")

    return redirect(url_for("customer_home"))

#booking a service request
@app.route("/customer/service/request", methods=["POST"])
def customer_service_request():
    service_id = request.form.get("service_id")
    professional_id = str(request.form.get("professional_id")) 
    customer_id = session.get('customer_id')  

    new_request = ServiceRequest(
        service_id=service_id,
        customer_id=customer_id,
        professional_id=professional_id,
        date_of_request=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        status="Requested"
    )

    db.session.add(new_request)
    db.session.commit()

    return redirect(url_for("customer_home"))

#displaying the service history following by updated status
@app.route("/customer/service/history", methods=["GET", "POST"])
def customer_service_history():
    customer_id = session.get('customer_id')  
    customer = Customer.query.get(customer_id)

    if request.method == "POST":
        service_request_id = request.form.get("service_request_id")
        rating = request.form.get("rating")
        remarks = request.form.get("remarks")

        service_request = ServiceRequest.query.get(service_request_id)

        if service_request:
            service_request.rating = int(rating) if rating else None
            service_request.remarks = remarks
            service_request.status = "Closed"  
            service_request.date_of_completion = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            db.session.commit()
            update_professional_average_rating(service_request.professional_id)
        return redirect(url_for('customer_service_history'))
    
    services = Service.query.all()
    services_with_professionals = []

    for service in services:
        professionals = Professional.query.filter_by(service_name=service.name, is_approved=True, is_blocked=False).all()
        services_with_professionals.append({
            "service": service,
            "professionals": professionals
        })

    service_history = ServiceRequest.query.filter_by(customer_id=customer_id).all()

    return render_template("cust_home.html",
                           service_history=service_history,
                           services_with_professionals=services_with_professionals,
                           customer=customer,
                           name=customer.fullname)


#customer search
@app.route("/customer/search", methods=["GET", "POST"])
def customer_search():
    cus_id = session.get('customer_id')
    if not cus_id:
        return redirect(url_for('user_login'))
    
    cus = Customer.query.get(cus_id)
    q = request.form.get('text_search', '').strip()
    searchby = request.form.get('searchby')

    search_results = []

    if searchby == "service":
        services = Service.query.filter(Service.name.ilike(f"%{q}%")).all()
        search_results = [
            {
                "service": service,
                "professionals": Professional.query.filter_by(service_name=service.name, is_approved=True, is_blocked=False).all()
            }
            for service in services
        ]
    elif searchby == "professional":
        search_results = ServiceRequest.query.join(
            Professional,
            ServiceRequest.professional_id == Professional.id
        ).filter(Professional.fullname.ilike(f"%{q}%"),
                 Professional.is_approved == True,
                 Professional.is_blocked == False,
                 ServiceRequest.customer_id == cus_id).all()

    elif searchby == "profiles":
        search_results = ServiceRequest.query.join(
            Professional,
            ServiceRequest.professional_id == Professional.id
        ).filter(
            Professional.fullname.ilike(f"%{q}%"),
            Professional.is_approved == True,
            Professional.is_blocked == False,
            ServiceRequest.status == "Closed").all()

    return render_template(
        "cust_search.html",
        name=cus.fullname,
        search_results=search_results,
        searchby=searchby
    )

#summary displaying the number of requests
@app.route("/customer/summary", methods=["GET", "POST"])
def customer_summary():
    cus_id = session.get('customer_id')
    if not cus_id:
        return redirect(url_for('user_login'))

    cus = Customer.query.get(cus_id)
    reqs = ServiceRequest.query.filter_by(customer_id=cus_id).all()

    # Initialize status counts
    counts = {
        "Closed": 0,
        "Requested": 0,
        "Accepted": 0,  # Adjust according to your data's naming
        "Rejected": 0
    }
    for req in reqs:
        counts[req.status] += 1

    # Labels and values for the bar chart
    labels = ['Closed', 'Requested', 'Accepted', 'Rejected']
    values = [counts["Closed"], counts["Requested"], counts["Accepted"], counts["Rejected"]]

    path = 'static/img/summaries/customer_summary.png'

    # Create the bar chart
    plt.bar(labels, values, color=['Pink']) 
    
    # Dynamically set y-ticks based on max value
    max_value = max(values)
    y_ticks = range(0, max_value + 2)  # +2 to ensure space above the highest bar
    plt.yticks(y_ticks)
    plt.ylim(0, max_value + 1)  # Set limit to max value +1 for better visualization

    plt.savefig(path)
    plt.clf()

    return render_template("cust_summary.html", name=cus.fullname, chart_path=path)



#professional home
@app.route("/professional/home", methods=["GET", "POST"])
def professional_home():
    pro_id = session.get('pro_id')
    if not pro_id:
        return redirect(url_for('user_login'))

    pro = Professional.query.get(pro_id)
    if not pro:
        flash('Professional not found.', 'error')
        return redirect(url_for('user_login'))

    service_requests = ServiceRequest.query.filter_by(professional_id=pro_id, status='Requested').all()
    closed_service_requests = ServiceRequest.query.filter_by(professional_id=pro_id, status='Closed').all()
    
    return render_template(
        "pro_home.html", 
        name=pro.fullname, 
        pro=pro,  
        service_requests=service_requests,
        closed_service_requests=closed_service_requests,
        average_rating=pro.avg_rating
    )

#professional profile
@app.route("/professional/update_profile", methods=["POST"])
def update_profile():
    pro_id = session.get('pro_id')
    if not pro_id:
        return redirect(url_for('user_login'))

    pro = Professional.query.get(pro_id)
    if pro:
        pro.fullname = request.form.get("fullname")
        pro.password = request.form.get("password")  # Hash if necessary
        pro.phone = request.form.get("phone")
        pro.experience = request.form.get("experience")
        pro.address = request.form.get("address")

        db.session.commit()
        flash("Profile updated successfully", "success")
    else:
        flash("Professional not found", "error")

    return redirect(url_for("professional_home"))

#professional accepting a service request
@app.route("/professional/accept/<int:service_request_id>", methods=["POST"])
def accept_service(service_request_id):
    pro_id = session.get('pro_id')
    if not pro_id:
        return redirect(url_for('user_login'))
    
    professional = Professional.query.get(pro_id) 

    ongoing_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        ServiceRequest.status == 'Accepted'  
    ).all()

    if ongoing_requests:
        flash('You cannot accept a new service request until your current request is closed.', 'danger')
        return redirect(url_for('professional_home')) 

    service_request = ServiceRequest.query.get(service_request_id)
    if service_request and service_request.status == 'Requested': 
        service_request.status = 'Accepted' 
        service_request.professional_id = professional.id 
        db.session.commit()
        flash('Service request accepted successfully!', 'success')
    else:
        flash('Unable to accept this service request.', 'danger') 
    return redirect(url_for('professional_home'))


#professional rejecting a service request
@app.route("/professional/reject/<int:service_request_id>", methods=["POST"])
def reject_service(service_request_id):
    service_request = ServiceRequest.query.get(service_request_id)
    if service_request:
        service_request.status = 'Rejected'
        db.session.commit()
        flash('Service request rejected successfully!', 'success')
    return redirect(url_for('professional_home'))

#professional search	
@app.route("/professional/search", methods=["GET", "POST"])
def professional_search():
    pro_id = session.get('pro_id')
    if not pro_id:
        return redirect(url_for('user_login'))
    
    pro = Professional.query.get(pro_id)    
    q = request.form.get('txt_search')
    search_by = request.form.get('search_by') 
    if not q:
        return render_template("pro_search.html", name=pro.fullname, search_results=[])
    search_results = []
    if search_by == "date":
        search_results = (
            ServiceRequest.query
            .filter(ServiceRequest.date_of_request.ilike(f"%{q}%"),
                    ServiceRequest.professional_id == pro_id)
            .join(Customer, ServiceRequest.customer_id == Customer.id).all()
        )
    elif search_by == "location":
        search_results = (
            ServiceRequest.query
            .join(Customer, ServiceRequest.customer_id == Customer.id)
            .filter(Customer.address.ilike(f"%{q}%"),
                    ServiceRequest.professional_id == pro_id).all()
        )
    elif search_by == "pincode":
        search_results = (
            ServiceRequest.query
            .join(Customer, ServiceRequest.customer_id == Customer.id)
            .filter(Customer.pincode.ilike(f"%{q}%"),
                    ServiceRequest.professional_id == pro_id).all()
        )

    return render_template("pro_search.html", name=pro.fullname, search_results=search_results) 
    
#professional summary
@app.route("/professional/summary", methods=["GET", "POST"])
def professional_summary():
    pro_id = session.get('pro_id')
    if not pro_id:
        return redirect(url_for('user_login'))
    
    pro = Professional.query.get(pro_id)
    reqs = ServiceRequest.query.filter_by(professional_id=pro_id).all()
    
    # Bar chart for service requests
    req_counts = {"Closed": 0, "Requested": 0, "Accepted": 0, "Rejected": 0}
    for req in reqs:
        req_counts[req.status] += 1
    
    req_labels = ['Closed', 'Requested', 'Accepted', 'Rejected']	
    req_values = [req_counts["Closed"], req_counts["Requested"], req_counts["Accepted"], req_counts["Rejected"]]
    bar_chart_path = 'static/img/summaries/professional_summary_bar.png'
    
    plt.bar(req_labels, req_values, width=0.5, color="pink")
    plt.savefig(bar_chart_path)
    plt.clf()

    return render_template("pro_summary.html", name=pro.fullname, bar_chart_path=bar_chart_path)

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('user_login', msg="Logged out successfully"))