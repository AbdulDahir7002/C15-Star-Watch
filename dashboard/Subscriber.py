"""Sets up the subscriber page."""
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
    """Runs the necessary functions for this page."""
    subscription_form()
    if st.button("Go to Unsubscribe Page"):
        st.session_state.show_unsubscribe = True
        st.rerun()


def validate_uk_mobile_number(phone_number):
    """Validates a phone number to ensure it fits UK numbers."""
    if phone_number[0:2] != "07":
        return "Please enter a valid phone number starting with 07"
    if len(phone_number) < 11 or len(phone_number) > 11:
        return "Please enter a valid phone number"
    return phone_number


def validate_email(email):
    """Validates the format of an email."""
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    if re.match(email_pattern, email):
        domain_part = email.split('@')[1]
        if '..' in domain_part:
            return False

        tld = domain_part.split('.')[-1]
        if len(tld) < 2 or not tld.isalpha():
            return False

        return True

    return False


def list_all_topics(sns):
    """Returns a list of all topics on AWS."""
    response = sns.list_topics()
    topics = []

    while "NextToken" in response:
        topics.extend(response["Topics"])
        response = sns.list_topics(NextToken=response["NextToken"])
    topics.extend(response["Topics"])
    return [topic["TopicArn"] for topic in topics]


def list_relevant_topics(all_topics: list) -> list:
    """Returns a list of starwatch topics on AWS."""
    return [topic for topic in all_topics if "c15-star-watch-" in topic]


def retrieve_chosen_topics(topic_list, city_list):
    """Returns a list of topics the user has chosen to subscribe to."""
    chosen_topics = [topic for topic in topic_list for city in city_list if bool(
        re.search(f".*({city})$", topic))]

    return chosen_topics


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
        sms_topics = retrieve_chosen_topics(
            topic_list, user_data["SMS"]["cities"])
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
            subscriptions = sns_client.list_subscriptions_by_topic(
                TopicArn=city_arn)

            for subscription in subscriptions['Subscriptions']:
                if subscription['Endpoint'] == endpoint:
                    sns_client.unsubscribe(
                        SubscriptionArn=subscription['SubscriptionArn'])
                    break
            else:
                st.warning(
                    f"No subscription found for {endpoint} on {city_arn}")
        except Exception as e:
            st.error(f"Error unsubscribing from {city_arn}: {e}")


def update_selectbox():
    """Updates the state of the subscription_type selectbox."""
    subscription_type = st.session_state.sub_type
    global user_data
    user_data = {}


def subscription_form():
    """The code for the subscribe functionality."""
    global user_data
    st.title("Subscription Form")
    st.write("Please provide your subscription details below.")

    subscription_type = st.selectbox(
        "Choose a subscription type", ["Newsletter", "Alerts"], key="sub_type", on_change=update_selectbox)

    if subscription_type == "Newsletter":
        email = st.text_input("Email Address")
        subscribed_topics = list_subscribed_topics(email, sns_client)
        if subscribed_topics:
            subscribed_cities = [get_city_from_arn(
                topic_arn) for topic_arn in subscribed_topics]
            cities = [
                city for city in city_options if city not in subscribed_cities]
        else:
            cities = city_options

        selected_cities = st.multiselect(
            "Select cities to subscribe to:", cities)
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


def get_city_from_arn(topic_arn):
    """Get the city associated with a specific arn"""
    arn_parts = topic_arn.split(":")
    city_name = arn_parts[5].replace("c15-star-watch-", "")
    return city_name


def get_city_topic_arn_mapping(sns_client):
    """Creates a mapping of cities to its corresponding arn."""
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


if __name__ == "__main__":
    app()
