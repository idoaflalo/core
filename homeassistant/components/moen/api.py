"""Api for Moen integration."""
import json
import threading
from typing import Callable, Tuple
import uuid

from awscrt import auth, io, mqtt
from awscrt.mqtt import Connection
from awsiot import mqtt_connection_builder
import boto3
from boto3.session import Session
from pycognito import Cognito

from .const import (
    APP_CLIENT_ID,
    APP_CLIENT_SECERT,
    COGNITO_IDP,
    ENDPOINT,
    IDENTITY_POOL_ID,
    REFRESH_TOKEN_INTERVAL,
    REGION_NAME,
    USER_POOL_ID,
)


class MoenApi:
    """A class for moen API."""

    def __init__(self, username: str, password: str):
        """Init Moen API."""
        super().__init__()
        self._username: str = username
        self._password: str = password
        self._lambda_client: Session.client = None
        self._mqtt_connection: Connection = None
        self._subscribers: dict = {}

    def connect(self) -> None:
        """Connect using the credentials."""
        self._start_refresh_credentials()

    def disconnect(self):
        """Disconnect from all open sockets."""
        self._mqtt_connection.disconnect()

    def authenticate(self) -> Tuple[str, str, str]:
        """Authenticate with moen servers."""
        cognito_obj = Cognito(
            USER_POOL_ID,
            APP_CLIENT_ID,
            client_secret=APP_CLIENT_SECERT,
            username=self._username,
        )

        cognito_obj.authenticate(password=self._password)

        cognito_identity_client = boto3.client(
            "cognito-identity", region_name=REGION_NAME
        )

        identity_id = cognito_identity_client.get_id(
            IdentityPoolId=IDENTITY_POOL_ID, Logins={COGNITO_IDP: cognito_obj.id_token}
        )["IdentityId"]

        credentials = cognito_identity_client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={COGNITO_IDP: cognito_obj.id_token},
        )["Credentials"]

        return (
            credentials["AccessKeyId"],
            credentials["SecretKey"],
            credentials["SessionToken"],
        )

    def _create_mqtt_connection(
        self, access_key_id, secret_access_key, session_token
    ) -> Connection:
        credentials_provider = auth.AwsCredentialsProvider.new_static(
            access_key_id, secret_access_key, session_token
        )

        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        return mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=ENDPOINT,
            client_bootstrap=client_bootstrap,
            region=REGION_NAME,
            credentials_provider=credentials_provider,
            client_id=str(uuid.uuid4()),
            clean_session=False,
            keep_alive_secs=6,
        )

    def _create_lambda_client(self, access_key_id, secret_access_key, session_token):
        return boto3.client(
            "lambda",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
            region_name=REGION_NAME,
        )

    def _start_refresh_credentials(self):
        credentials = self.authenticate()

        if self._mqtt_connection:
            self._mqtt_connection.disconnect()
        self._mqtt_connection = self._create_mqtt_connection(*credentials)
        self._mqtt_connection.connect()

        for topic, callback_set in self._subscribers.items():
            for callback in callback_set:
                self.subscribe_to_topic(topic, callback)

        self._lambda_client = self._create_lambda_client(*credentials)
        threading.Timer(REFRESH_TOKEN_INTERVAL, self._start_refresh_credentials).start()

        return credentials

    def invoke_lambda_function(self, function_name: str, payload: dict = None):
        """Invoke a given function in the lambda client."""
        result = self._lambda_client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=b"" if not payload else json.dumps(payload).encode(),
        )

        return json.load(result["Payload"])["body"]

    def subscribe_to_topic(self, topic: str, callback: Callable):
        """Subscribe a given topic."""
        self._mqtt_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback,
        )

        self._subscribers.setdefault(topic, set()).add(callback)
