from flask import Blueprint, render_template, Response, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .data_model import Insight

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
