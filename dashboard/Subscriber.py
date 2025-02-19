import streamlit as st
import boto3
import re

sns_client = boto3.client("sns", region_name="eu-west-2")
user_data = {}

city_options = [
    "Aberdeen", "Armagh", "Bangor", "Bath", "Belfast", "Birmingham", "Bradford",
    "Brighton-and-Hove", "Bristol", "Cambridge", "Canterbury", "Cardiff", "Carlisle",
    "Chelmsford", "Chester", "Chichester", "Colchester", "Coventry", "Derby",
    "Doncaster", "Dundee", "Dunfermline", "Durham", "Edinburgh", "Ely", "Exeter",
    "Glasgow", "Gloucester", "Hereford", "Inverness", "Kingston-upon-Hull",
    "Lancaster", "Leeds", "Leicester", "Lichfield", "Lincoln", "Lisburn",
    "Liverpool", "London", "Londonderry", "Manchester", "Milton-Keynes",
    "Newcastle-upon-Tyne", "Newport", "Newry", "Norwich", "Nottingham", "Oxford",
    "Perth", "Peterborough", "Plymouth", "Portsmouth", "Preston", "Ripon",
    "Salford", "Salisbury", "Sheffield", "Southampton", "Southend-on-Sea",
    "St-Albans", "St-Asaph", "St-Davids", "Stirling", "Stoke-on-Trent",
    "Sunderland", "Swansea", "Truro", "Wakefield", "Wells", "Westminster",
    "Winchester", "Wolverhampton", "Worcester", "Wrexham", "York"
]


def app():
    subscription_form()
    unsubscribe_form(sns_client)



def validate_uk_mobile_number(phone_number):
    if phone_number[0:2] != "07":
        return "Please enter a valid phone number starting with 07"
    if len(phone_number) < 11 or len(phone_number) > 11:
        return "Please enter a valid phone number"
    return phone_number


def validate_email(email):
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_pattern, email) is not None


def list_all_topics(sns):
    """Returns a list of all topics on AWS."""
    response = sns.list_topics()
    topics = []
    while True:
        topics.extend(response["Topics"])
        if "NextToken" in response:
            response = sns.list_topics(NextToken=response["NextToken"])
        else:
            break
    return [topic["TopicArn"] for topic in topics]

def list_relevant_topics(all_topics: list) -> list:
    """Returns a list of starwatch topics on AWS."""
    return [topic for topic in all_topics if "c15-star-watch-" in topic]


def retrieve_chosen_topics(topic_list, city_list):
    """Returns a list of topics the user has chosen to subscribe to."""
    return [topic for topic in topic_list for city in city_list if city in topic]


def subscribe_user(user_data, topic_list, sns):
    """Subscribes a user to chosen topic(s)."""
    if "email" in user_data.keys():
        email_topics = retrieve_chosen_topics(
            topic_list, user_data["email"]["cities"])
        for topic in email_topics:
            response = sns.subscribe(
                TopicArn=topic,
                Protocol="email",
                Endpoint=user_data["email"]["address"],
                ReturnSubscriptionArn=True
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                return f"Could not subscribe user to {topic}."
        
    elif "SMS" in user_data.keys():
        sms_topics = retrieve_chosen_topics(topic_list, user_data["SMS"]["cities"])
        for topic in sms_topics:
            response = sns.subscribe(
                TopicArn=topic,
                Protocol="sms",
                Endpoint=user_data["SMS"]["number"],
                ReturnSubscriptionArn=True
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                return f"Could not subscribe user to {topic}."
        return "Subscribed!"


def list_subscribed_topics(email, sns):
    """Returns a list of subscribed topics."""
    response = sns.list_subscriptions()
    subscriptions = []
    while True:
        subscriptions.extend(response["Subscriptions"])

        if "NextToken" in response:
            response = sns.list_subscriptions(NextToken=response["NextToken"])
        else:
            break

    valid_subscriptions = [
        s["SubscriptionArn"] for s in subscriptions if s["Endpoint"] == email
        and s["SubscriptionArn"] not in ["Deleted", "PendingConfirmation"]]

    return valid_subscriptions


def unsubscribe_user(cities_to_unsubscribe, sns_client, endpoint):
    """Unsubscribes user from selected topics."""
    if len(cities_to_unsubscribe) == 0:
        return "You are not subscribed to any topics!"
    
    for city_arn in cities_to_unsubscribe:
        try:
            subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=city_arn)
            
            for subscription in subscriptions['Subscriptions']:
                if subscription['Endpoint'] == endpoint:
                    sns_client.unsubscribe(SubscriptionArn=subscription['SubscriptionArn'])
                    break
            else:
                st.warning(f"No subscription found for {endpoint} on {city_arn}")
        except Exception as e:
            st.error(f"Error unsubscribing from {city_arn}: {e}")



def update_selectbox():
    subscription_type = st.session_state.sub_type
    global user_data
    user_data = {}


def subscription_form():
    global user_data
    st.title("Subscription Form")
    st.write("Please provide your subscription details below.")

    subscription_type = st.selectbox(
        "Choose a subscription type", ["Newsletter", "Alerts"], key="sub_type", on_change=update_selectbox)

    if subscription_type == "Newsletter":
        email = st.text_input("Email Address")
        selected_cities = st.multiselect(
            "Select cities to subscribe to:", city_options)
        submit_button = st.button(label="Subscribe")
        if submit_button:
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return
            user_data.setdefault("email", {})["address"] = email
            user_data.setdefault("email", {})["cities"] = selected_cities
            all_topics = list_all_topics(sns_client)
            relevant_topics = list_relevant_topics(all_topics)
            subscribe_user(user_data, relevant_topics, sns_client)
            st.success(
                f"Thank you! You've been successfully subscribed to the newsletter for {', '.join(selected_cities)}. Please check your email inbox to confirm the subscription.")

    elif subscription_type == "Alerts":
        phone_number = st.text_input("Phone Number (+44)")
        selected_cities = st.multiselect(
            "Select cities to subscribe to:", city_options)
        submit_button = st.button(label="Subscribe")
        if submit_button:
            validation_result = validate_uk_mobile_number(phone_number)
            if validation_result != phone_number:
                st.error(validation_result)
                return
            user_data.setdefault("SMS", {})["number"] = phone_number
            user_data.setdefault("SMS", {})["cities"] = selected_cities

            all_topics = list_all_topics(sns_client)
            relevant_topics = list_relevant_topics(all_topics)
            subscribe_user(user_data, relevant_topics, sns_client)
            st.success(
                f"Thank you! You've been successfully subscribed to SMS alerts for {', '.join(selected_cities)}.")


def update_unsub_selectbox():
    service_type = st.session_state.unsub_type
    global user_data
    user_data = {}


def get_city_from_arn(topic_arn):
    arn_parts = topic_arn.split(":")
    city_name = arn_parts[5].replace("c15-star-watch-", "")
    return city_name

def get_city_topic_arn_mapping(sns_client):
    city_to_arn_mapping = {}

    response = sns_client.list_topics()
    while True:
        for topic in response["Topics"]:
            arn = topic["TopicArn"]
            if arn.startswith("arn:aws:sns:eu-west-2:129033205317:c15-star-watch"):
                city_name = get_city_from_arn(arn)
                city_to_arn_mapping[city_name] = arn

        if "NextToken" in response:
            response = sns_client.list_topics(NextToken=response["NextToken"])
        else:
            break
    return city_to_arn_mapping

def unsubscribe_form(sns_client):
    st.title("Unsubscribe Form")
    st.write("Please provide your subscription details below.")

    service_type = st.selectbox(
        "Choose a subscription type", ["Newsletter", "Alerts"], key="unsub_type")
    city_arn_mapping = get_city_topic_arn_mapping(sns_client)

    if service_type == "Newsletter":
        email = st.text_input("Email Address", key="unsub_email")
        if email:
            subscribed_topics = list_subscribed_topics(email, sns_client)
            if subscribed_topics:
                subscribed_cities = [get_city_from_arn(topic_arn) for topic_arn in subscribed_topics]
                
                cities_to_unsubscribe = st.multiselect(
                    "Select cities to unsubscribe from", subscribed_cities)
                
                submit_button = st.button(label="Unsubscribe")
                if submit_button:
                    if cities_to_unsubscribe:
                        topic_arns_to_unsubscribe = [
                            city_arn_mapping[city] for city in cities_to_unsubscribe if city in city_arn_mapping
                        ]
                        if topic_arns_to_unsubscribe:
                            unsubscribe_user(topic_arns_to_unsubscribe, sns_client, email)
                        st.success(f"You have been unsubscribed from {', '.join(cities_to_unsubscribe)}.")
                    else:
                        st.warning("Please select at least one city to unsubscribe from.")
            else:
                st.warning("You are not subscribed to any newsletters.")

    elif service_type == "Alerts":
        phone_number = st.text_input("Phone Number (+44)", key="unsub_no")
        if phone_number:
            subscribed_topics = list_subscribed_topics(phone_number, sns_client)
        
            if subscribed_topics:
                subscribed_cities = [get_city_from_arn(topic_arn) for topic_arn in subscribed_topics]
                
                cities_to_unsubscribe = st.multiselect(
                    "Select cities to unsubscribe from", subscribed_cities)
                
                submit_button = st.button(label="Unsubscribe")
                if submit_button:
                    if cities_to_unsubscribe:
                        for city in cities_to_unsubscribe:
                            topic_arn_to_unsubscribe = city_arn_mapping.get(city)
                            if topic_arn_to_unsubscribe:
                                unsubscribe_user([topic_arn_to_unsubscribe], sns_client, phone_number)
                        st.success(f"You have been unsubscribed from {', '.join(cities_to_unsubscribe)}.")
                    else:
                        st.warning("Please select at least one city to unsubscribe from.")
            else:
                st.warning("You are not subscribed to any alerts.")





if __name__ == "__main__":
    app()