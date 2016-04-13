"""
Simple Alexa skill that reads the estimated time in traffic based on predefined
start and end addresses.
"""
from __future__ import print_function
import googlemaps
import datetime

# Populate with your Alexa skill's application ID to prevent someone else
# from configuring a skill that sends requests to this function.
APP_ID = ""

# Put your Google Maps API key here
GMAPS_API_KEY = ""

# Dictionary mapping names of people to their addresses.
# Customize with your own values.
PEOPLE_AND_PLACES = {
    "Mark": {
        "work": {
            "address": "1 Hacker Way, Menlo Park, CA 94025",
            "start": "home"
        },
        "home": {
            "address": "3660 21st St, San Francisco, CA 94114",
            "start": "work"
        }
    },
    "Tim": {
        "work": {
            "address": "1 Infinite Loop, Cupertino, CA 95014",
            "start": "home"
        },
        "home": {
            "address": "Webster St, Palo Alto, CA ",
            "start": "work"
        },
        "cafe": {
             "address": "10591 N De Anza Blvd, Cupertino, CA 95014",
             "start": "work"
        }
    }
}

# Default if skill is launched without specifying a person
DEFAULT_PERSON = "Mark"

# ------------------------------------------------------------------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if APP_ID and event['session']['application']['applicationId'] != APP_ID:
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AMAZON.HelpIntent":
        return get_help_response(intent, session)
    elif intent_name == "AMAZON.CancelIntent":
        return get_cancel_response(intent, session)
    elif intent_name == "GetTrafficIntent":
        return get_traffic(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """Welcome message when the skill is launched"""
    session_attributes = {}
    card_title = "Traffic Time"
    speech_output = "Hello, I can help you lookup the estimated time in " \
                    "traffic. For example, you can say, " \
                    "how's the traffic to work."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Sorry, I didn't understand what you said. " \
                    "Please tell me what traffic to check. " \
                    "For example, you can say, " \
                    "how's the traffic to work."

    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_help_response(intent, session):
    """Response given when the user asks for help"""
    card_title = "Traffic Time Help"
    session_attributes = session.get('attributes', {})
    should_end_session = False

    speech_output = "I can help you lookup the estimated time in traffic. " \
                    "For example, you can say, how's the traffic to work. " \
                    "You can also include the name of the person. " \
                    "For example, you can say, " \
                    "how's the traffic to work for {}".format(DEFAULT_PERSON)

    reprompt_text = "Sorry, I didn't understand what you said. " \
                    "Please tell me what traffic to check. " \
                    "For example, you can say, " \
                    "how's the traffic to work."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_cancel_response(intent, session):
    """Response given when the user cancels the skill"""
    card_title = "Goodbye"
    session_attributes = session.get('attributes', {})
    should_end_session = True
    speech_output = "OK, goodbye"
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def error_response(intent, session):
    """Response given when an unexpected error occurs"""
    card_title = "Oops"
    session_attributes = session.get('attributes', {})
    should_end_session = False
    speech_output = "Sorry, I didn't understand what you said. " \
                    "Please try again."
    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def place_not_found(intent, session, person, place):
    """
    Response given when the name of the place is not found in the
    predefined data.
    """
    card_title = "Place Not Found"
    session_attributes = session.get('attributes', {})
    should_end_session = False
    speech_output = "Sorry, I couldn't find the place, {}, for {}. " \
                    "Please try again.".format(place, person)
    reprompt_text = "Sorry, I didn't understand what you said. " \
                    "Please try again."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def person_not_found(intent, session, person):
    """
    Response given when the name of the person is not found in the
    predefined data.
    """
    card_title = "Person Not Found"
    session_attributes = session.get('attributes', {})
    should_end_session = False
    speech_output = "Sorry, I don't know who is {}. " \
                    "Please try again.".format(person)
    reprompt_text = "Sorry, I didn't understand what you said. " \
                    "Please try again."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_traffic(intent, session):
    """
    The main function that looks up the estimated traffic times.
    """
    card_title = "Traffic Time"
    session_attributes = session.get('attributes', {})
    should_end_session = False

    if 'slots' not in intent:
        print('ERROR: Intent did not have any slots')
        return error_response(intent, session)

    # Get the name of the person, or set it to the default person
    try:
        person = intent['slots']['Person']['value'] or DEFAULT_PERSON
    except KeyError:
        person = DEFAULT_PERSON

    # Check if the person is in the predefined data
    if person not in PEOPLE_AND_PLACES.keys():
        print("ERROR: Person {} not found".format(person))
        return person_not_found(intent, session, person)

    try:
        dest = intent['slots']['Destination']['value']
    except KeyError:
        dest = None

    # Destination is a required slot value. Return error if it is not found.
    if not dest:
        print("ERROR: Failed to get Destination from intent")
        return error_response(intent, session)

    # Check if the destination place's name is in the predefined data for
    # the person specified.
    if dest not in PEOPLE_AND_PLACES[person].keys():
        print("ERROR: dest '{}' not in person '{}' list of places".format(
            dest, person))
        return place_not_found(intent, session, person, dest)

    # Check if there is a start location
    try:
        start = intent['slots']['Start']['value']
    except KeyError:
        start = None

    # If no start place is provided, lookup the default start place for the
    # destination place provided.
    if not start:
        start = PEOPLE_AND_PLACES[person][dest]['start']

    # Check if the start place's name is in the predefined data for the person.
    if start not in PEOPLE_AND_PLACES[person].keys():
        print("ERROR: start '{}' not in person '{}' list of places".format(
            start, person))
        return place_not_found(intent, session, person, start)

    # Corner case where user says the same place for both start and destination
    if start == dest:
        speech_output = "It's probably not a good idea to stay in one place " \
                        "for too long. Please try again with two different " \
                        "places. You can say something like, " \
                        "how's the traffic to work from home."

        reprompt_text = "Sorry, I didn't understand what you said. " \
                        "Please try again."

        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    # Lookup the start and dest addresses
    start_addr = PEOPLE_AND_PLACES[person][start]['address']
    dest_addr = PEOPLE_AND_PLACES[person][dest]['address']

    # Use Google Maps API client to get directions
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    departure_time = datetime.datetime.now()

    # Default directions
    res_1 = gmaps.directions(
        start_addr, dest_addr, departure_time=departure_time)

    # Alternate directions avoiding highways
    res_2 = gmaps.directions(start_addr, dest_addr,
        departure_time=departure_time, avoid=['highways'])

    # Get the traffic time in minutes for both routes
    mins_1 = res_1[0]['legs'][0]['duration_in_traffic']['value'] / 60
    mins_2 = res_2[0]['legs'][0]['duration_in_traffic']['value'] / 60

    speech_output = "Your drive to {} ".format(dest)
    if start:
        speech_output += "from {} ".format(start)

    speech_output += "will take approximately {mins_1} minutes. " \
                     "If you avoid highways, it will take about {mins_2} " \
                     "minutes.".format(mins_1=mins_1, mins_2=mins_2)
    reprompt_text = None
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
