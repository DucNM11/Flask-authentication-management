from flask import Blueprint, render_template, Response, request, flash, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from . import db
from .data_model import Insight, User

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render template for index page
    """
    return render_template("index.html")


@main.route("/profile")
@login_required
def profile():
    """Render template for profile
    """
    return render_template("profile.html", user_name=current_user.name)

@main.route("/delete_user")
@login_required
def delete_user():
    """ Render template for Deleting user details
    """
    return render_template("delete_user.html")

@main.route("/delete_user", methods=["POST"])
@login_required
def delete_user_post():
    """ To delete user details from the mysql db
    """
    if request.method == "POST":
        pwd = request.form["pwd"]

        user = User.query.filter_by(email=current_user.email).first()
        db.session.commit()
        if not user or not check_password_hash(user.password, pwd):
            flash('Please check your login detail and try again.')
            return redirect(url_for("main.delete_user"))
        else:
            result = User.query.filter_by(email=current_user.email).delete()
            db.session.commit()
            if not result:
                flash("User deletion failed. Try Again!!")
                return redirect(url_for("main.delete_user"))
            else:
                return render_template("index.html")
    return render_template("delete_user.html")


@main.route("/reset_pwd")
@login_required
def reset_pwd():
    """ Render template for to reset user password
    """
    return render_template("reset_pwd.html")

@main.route("/reset_pwd", methods=["POST"])
@login_required
def reset_pwd_post():
    """ To reset user password detail from the mysql db
    """
    if request.method == "POST":
        newpwd = request.form["newpwd"]
        newpwd2 = request.form["newpwd2"]
        if newpwd != newpwd2:
            flash("Re-type Password")
            return redirect(url_for("main.reset_pwd"))
        email = current_user.email
        new_password = generate_password_hash(newpwd2, method="sha256")
        result = User.query.filter(User.email==email).update({"password": new_password})
        db.session.commit()
        if not result:
            flash("Password update failed. Try Again!!")
            return redirect(url_for("main.reset_pwd"))
        else:
            flash("Update Successful")
            return render_template("login.html")
    return render_template("reset_pwd.html")

@main.route("/profile", methods=["POST"])
@login_required
def profile_post():
    """POST method to get request from customer to return requested data on profile detail page
    """
    symbol = request.form.get("symbol")
    data = Insight.query.filter_by(symbol=symbol).first()

    if data is None:
        flash("Data on this cryptocurrency is unavailable")
        return redirect(url_for("main.profile"))

    return render_template(
        "profile_detail.html",
        slug=data.slug.replace('\'', ''),
        num_market_pairs=data.num_market_pairs,
        date_added=data.date_added,
        cmc_rank=data.cmc_rank,
        last_updated=data.last_updated,
        quote_GBP_price=data.quote_GBP_price,
        quote_GBP_volume_24h=data.quote_GBP_volume_24h,
        quote_GBP_volume_change_24h=data.quote_GBP_volume_change_24h,
        quote_GBP_percent_change_1h=data.quote_GBP_percent_change_1h,
        quote_GBP_percent_change_24h=data.quote_GBP_percent_change_24h,
        sentiment=data.sentiment,
        popularity=data.popularity)
