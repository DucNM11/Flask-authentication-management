# Cloud Computing Mini Project ECS781P
## Group 25 - Crypto Summariser

Crypto Summariser is an API which provides users a secure way of accessing a unified source of information about crypto coins. Users can sign up for an account, which is protected by SHA256 hashed authentication, and once authenticated can query up-to-date information on the current top cryptocoins over https. The information is collected from the CoinMarketCap and Twitter external APIs and where it is stored in a Cloud SQL database in order to be quickly queried by the user. 

![arch](https://user-images.githubusercontent.com/37650605/162621233-fa1fcb96-ce28-469e-81b4-0aa590e137ec.jpeg)

## 1. Dynamically REST API
The Crypto Summariser aims to provide the user with a sufficient range of APIs for their needs. At the moment, we have implemented 5 APIs that cover all the CRUD operations from creating a new user, reading info for authenticating the current user/providing them with our summarized data, updating their password, and deleting the current user. This data is hashed and stored on a Cloud SQL instance, ready to serve to the user. 

#### Create operation - dynamically gets data from the form and feedbacks to the customer about their input
```
@auth.route("/signup", methods=["POST"])
def signup_post():
    """POST method to get customer's information from the form to check for duplication
    and sign up
    
    # Dynamically getting customer's information from the front end
    # Get required data from the form
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    # Check for duplication
    user = User.query.filter_by(email=email).first()

    # Notify customer if the email is already registered
    if user:
        flash("Email already exists")
        return redirect(url_for("auth.signup"))
```
#### Reading operation - dynamically gets data from the form and feedbacks to the customer about their input
```
@auth.route("/login", methods=["POST"])
def login_post():
    """POST method to get input data from customer for authentication
    """
    # Get required data from the form
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    # Check for duplication
    user = User.query.filter_by(email=email).first()

    # Notify customer if the authentication step is fail
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login detail and try again.')
        return redirect(url_for("auth.login"))

    # Authentication step is successful, redirect to the user's profile page
    login_user(user, remember=remember)
    return redirect(url_for("main.profile"))
```
#### Update operation - dynamically gets data from the form and feedbacks to the customer about their input
````
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
````

#### Delete operation - dynamically gets data from the form and feedbacks to the customer about their input
````
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
````

## 2. External APIs
The Crypto Summariser aims to consolidate information from multiple external sources and provide it to the user in a single call. At the moment, we have implemented two data sources using the CoinMarketCap and Twitter public APIs. This data is collected and pushed to a Cloud SQL instance, ready to serve to the user. 

We start by querying the top 20 coins, by current market cap, from the CoinMarketCap API where we retrieve the coin metadata:(symbol, name, rank etc.) as well as some basic financial infomration: ['quote_GBP_price','quote_GBP_volume_24h','quote_GBP_volume_change_24h','quote_GBP_percent_change_1h','quote_GBP_percent_change_24h'].

With this list of top coins, we additionaly use the Twitter API to get the current sentiment and popularity of the coin. This is implemented by first retrieving the latest 100 tweets which mention the coin's name, filter for english-only tweets, remove stopwords:
```
response = client.search_recent_tweets(
        searchstring,
        max_results=100,
    )
    tweets = response.data
    # cleaning:
    stopwords = nltk.corpus.stopwords.words("english")
    for tweet in tweets:
        if detect(tweet.text) != "en":
            tweets.remove(tweet)
        else:
            tokens = nltk.tokenize.word_tokenize(tweet.text)
            tokens_cleaned = [word for word in tokens if word.isalpha()]
            tokens_cleaned = [
                word for word in tokens_cleaned if word.lower() not in stopwords
            ]
            tweet.text = (" ").join(tokens_cleaned)

    return tweets
```
We then perform some basic sentiment analysis, using the NLTK library, to get a current average sentiment:

```
def getaveragesentiment(tweets):
    """for a list of tweets, get the average sentiment of each 
        tweet. 
    """
    
    tweetsentiment = 0
    sia = SentimentIntensityAnalyzer()
    for tweet in tweets:
        sentiment = sia.polarity_scores(tweet.text)
        tweetsentiment = tweetsentiment + sentiment["pos"] - sentiment["neg"]

    tweetsentiment = tweetsentiment / len(tweets)

    return tweetsentiment
```

Additionally, we compute a popiarity score, which is a measure of the frequency of Tweets - the inverse of the amount of time between the 1st and 100th most recent Tweets. This is then normalised by the frequency of bitcoin tweets, such that values over 1 are being tweeted about more frequently that bitcoin, and below 1 is less frequently:

```
    btc_popularity = 1 / (btc_tweets[0].id - btc_tweets[-1].id)
    popularity = (1 / (tweets[0].id - tweets[-1].id)) / btc_popularity

    return popularity
```

Once the table has been populated with both sources of info, it is pushed to the cloud sql instance, ready to be served to the user of our Crypto Summariser app. In this proof of concept, we have simply run the code in advance to populate the table in the database, however in production we would run this as a cron job e.g. every 5 mins to provide the most up-to-date info to the user:

```
5 * * * * ./coinmarketapi.py
````

## 3. Cloud database for accessing persistent information
The Crypto Summariser aims to provide secured services through Google Cloud Platform Database to the customers. At the moment, we have implemented our server's database on Google Cloud MySQL to store our customer data.

## 4. Security measures
The Crypto Summariser aims to provide secured services to the customers. At the moment, we have implemented four security measures on our app to make sure to put customers at ease.
#### Application serving over https

Our application supports connection through HTTPS protocol with our certificate stored securely on the server.
```
#!/usr/bin/env bash

export FLASK_APP=app_auth
export FLASK_DEBUG=1
python -m flask run --cert=cert.pem --key=key.pem

````

#### User accounts and access management with hash-based authentication

All customers' passwords is stored after being hashed.
```
# Register customer information into the system
new_user = User(email=email,
                name=name,
                password=generate_password_hash(password, method="sha256"))
...
# To reset user password
new_password = generate_password_hash(newpwd2, method="sha256")
````

#### Securing the database with role-based policies
On our Google Cloud Database instance, we make sure to create role-based policies so that only authorized service user with the right role and secret key has the right to interact with it. The authorized service account is securely stored in a .env file on our server.

````
DOTENV_FILE = '.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))

...

# Google Cloud SQL (change this accordingly)
PASSWORD = env_config.get("PASSWORD")
PUBLIC_IP_ADDRESS = env_config.get("PUBLIC_IP_ADDRESS")
DBNAME = env_config.get("DBNAME")
PROJECT_ID = env_config.get("PROJECT_ID")
INSTANCE_NAME = env_config.get("INSTANCE_NAME")

# configuration
app.config["SECRET_KEY"] = env_config.get("SECRET_KEY")
app.config[
    "SQLALCHEMY_DATABASE_URI"] = f'mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}'
````
Furthermore, to add one more security layer on top of role-based policies from our database. We utilized the GCP function on connections management, even with the right authentication information for the service account, the client VM instance needs to be in the authorized IP list to access our database. For this to work, this required a setup for a static IP from GCP Compute Engine Service. This security feature could be further developed into the GCP's IAM method in our future work for scalability. 
![image](https://user-images.githubusercontent.com/14797495/162697839-de1d8eae-c782-4582-9aa2-ed2e148f9337.png)

## 5. Scalability
Developing this app with a mindset for it to be easily scaled out, we developed a docker image to ensure its required environments no matter which platforms.
````
FROM python:3.8.10-alpine

WORKDIR /app
COPY . /app

RUN apk --no-cache update \
 && apk add --no-cache  mariadb-connector-c-dev \
                        python3-dev \
                        gpgme-dev \
                        build-base \
 && pip install -r requirements.txt

ENV FLASK_APP=app_auth
ENV FLASK_DEBUG=1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80", "--cert=cert.pem", "--key=key.pem"]
EXPOSE 80
````

To further optimize the workflow, we created a load-env.sh file to automate the whole process.
````
#!/usr/bin/env bash

docker image build . -t=auth_app
docker run -dp 80:80 flask_auth
````

For a quick run in development process, it could be done by the shell script start_app.sh.
````
#!/usr/bin/env bash

export FLASK_APP=app_auth
export FLASK_DEBUG=1
python -m flask run --cert=cert.pem --key=key.pem

````
