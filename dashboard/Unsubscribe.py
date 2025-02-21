import streamlit as st
import boto3
from Subscriber import get_city_topic_arn_mapping, list_subscribed_topics, get_city_from_arn, unsubscribe_user

sns_client = boto3.client("sns", region_name="eu-west-2")
user_data = {}


def app():
    """Runs the necessary code for this page."""
    if st.session_state.show_unsubscribe:
        unsubscribe_form(sns_client)
    else:
        st.warning(
            "Please go to the Subscribe page and click 'Go to Unsubscribe Page' to unsubscribe.")


def unsubscribe_form(sns_client):
    """The function that allows a user to unsubscribe."""
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
                subscribed_cities = [get_city_from_arn(
                    topic_arn) for topic_arn in subscribed_topics]

                cities_to_unsubscribe = st.multiselect(
                    "Select cities to unsubscribe from", subscribed_cities)

                submit_button = st.button(label="Unsubscribe")
                if submit_button:
                    if cities_to_unsubscribe:
                        topic_arns_to_unsubscribe = [
                            city_arn_mapping[city] for city in cities_to_unsubscribe if city in city_arn_mapping
                        ]
                        if topic_arns_to_unsubscribe:
                            unsubscribe_user(
                                topic_arns_to_unsubscribe, sns_client, email)
                        st.success(
                            f"You have been unsubscribed from {', '.join(cities_to_unsubscribe)}.")
                    else:
                        st.warning(
                            "Please select at least one city to unsubscribe from.")
            else:
                st.warning("You are not subscribed to any newsletters.")

    elif service_type == "Alerts":
        phone_number = st.text_input("Phone Number (+44)", key="unsub_no")
        if phone_number:
            subscribed_topics = list_subscribed_topics(
                phone_number, sns_client)

            if subscribed_topics:
                subscribed_cities = [get_city_from_arn(
                    topic_arn) for topic_arn in subscribed_topics]

                cities_to_unsubscribe = st.multiselect(
                    "Select cities to unsubscribe from", subscribed_cities)

                submit_button = st.button(label="Unsubscribe")
                if submit_button:
                    if cities_to_unsubscribe:
                        for city in cities_to_unsubscribe:
                            topic_arn_to_unsubscribe = city_arn_mapping.get(
                                city)
                            if topic_arn_to_unsubscribe:
                                unsubscribe_user(
                                    [topic_arn_to_unsubscribe], sns_client, phone_number)
                        st.success(
                            f"You have been unsubscribed from {', '.join(cities_to_unsubscribe)}.")
                    else:
                        st.warning(
                            "Please select at least one city to unsubscribe from.")
            else:
                st.warning("You are not subscribed to any alerts.")


if __name__ == "__main__":
    app()
