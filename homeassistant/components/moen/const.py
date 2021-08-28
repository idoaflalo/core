"""Constants for the Moen integration."""

DOMAIN = "moen"

ATTR_API = "api"
ATTR_DEVICE_LIST = "device-list"

TITLE_FIELD = "title"
USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"

REFRESH_TOKEN_INTERVAL = 55 * 60

REGION_NAME = "us-east-2"
USER_POOL_ID = "us-east-2_9puIPVyv1"
APP_CLIENT_ID = "6qn9pep31dglq6ed4fvlq6rp5t"
APP_CLIENT_SECERT = "lpthklgkgthtg77rblqbvc8qu894n6ugei8db9th350g4l3g8id"
COGNITO_IDP = "cognito-idp.us-east-2.amazonaws.com/us-east-2_9puIPVyv1"
IDENTITY_POOL_ID = "us-east-2:7880fbef-a3a8-4ffc-a0d1-74e686e79c80"
ENDPOINT = "a1r2q5ic87novc-ats.iot.us-east-2.amazonaws.com"

MQTT_UPDATE_ACCEPTED_TOPIC = "$aws/things/{}/shadow/update/accepted"

LAMBDA_GET_DEVICES = "smartwater-app-device-api-prod-list"
LAMBDA_UPDATE_SHADOW = "smartwater-app-shadow-api-prod-update"
