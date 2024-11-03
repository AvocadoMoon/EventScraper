import json

import requests
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from src.logger import create_logger_from_designated_logger
from src.publishers.mobilizon.gql_requests import EventGQL, AuthenticationGQL, ActorsGQL
from src.publishers.mobilizon.types import MobilizonEvent, Actor

logger = create_logger_from_designated_logger(__name__)


class retry_if_not_exception_type(retry_if_exception):
    """Retries except an exception has been raised of one or more types."""

    def __init__(self, exception_types=Exception):
        self.exception_types = exception_types
        super(retry_if_not_exception_type, self).__init__(
            lambda e: not isinstance(e, exception_types))



# Single under score signifies hidden in python

class _MobilizonClient:
    class LoginTokens:
        accessToken: str
        refreshToken: str

        def __init__(self, access_token: str, refresh_token: str):
            self.accessToken = access_token
            self.refreshToken = refresh_token

    loginTokens: LoginTokens = None
    client: Client = None
    endpoint: str = None
    
    def __init__(self, endpoint: str, email: str, password: str):
        self.endpoint = endpoint
        self.client = self._build_client()
        data = self.publish(AuthenticationGQL.loginGQL(email, password))
        login = data['login']
        self.loginTokens = self.LoginTokens(login['accessToken'], login['refreshToken'])
        self.client = self._build_client(self.loginTokens.accessToken)
    
    def _build_client(self,bearer=None):
        headers = dict()
        if bearer is not None:
            headers['Authorization'] = 'Bearer ' + bearer
        transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=headers,
            verify=True,
            # retries=3,
        )
        return Client(transport=transport, fetch_schema_from_transport=True)
        
    
    def refresh_token(self, refresh_token: str):
        return self.publish(AuthenticationGQL.refreshTokenGQL(refresh_token))
    
    def logOut(self):
        return self.publish(AuthenticationGQL.logoutGQL(f'"{self.loginTokens.refreshToken}"'))  # void

    
    # attempts at 0s, 2s, 4s, 8s
    @retry(reraise=True, stop=stop_after_attempt(4),
           wait=wait_exponential(multiplier=2))
    def publish(self, query, file:bool = False, params: dict = None):
        response = self.client.execute(query) if not file else self.client.execute(query, variable_values=params, upload_files=True)
        return response



class MobilizonAPI:
    _mobilizon_client: _MobilizonClient
    bot_actor: Actor
    
    def __init__(self, endpoint: str, email: str, password: str):
        self._mobilizon_client = _MobilizonClient(endpoint, f'"{email}"', f'"{password}"')
        self.bot_actor = Actor(**self.getActors()["identities"][0])
        logger.info("Logged In Mobilizon")
    # events
        
    
    def bot_created_event(self, event_type: MobilizonEvent) -> dict:
        event_type.organizerActorId = self.bot_actor.id
        # print(EventGQL.createEventGQL(event_type))

        eventID = self._mobilizon_client.publish(EventGQL.createEventGQL(event_type))
        return {"id": eventID["createEvent"]["id"], "uuid": eventID["createEvent"]["uuid"]}
    
    def upload_file(self, name: str, file):
        variables = {"name": "Duck.jpg", "file": "theFiles", "actorID": self.bot_actor.id}
        variables = json.dumps(variables)
        response = requests.post(self._mobilizon_client.endpoint, 
            files=(
                # Name Filename data content_type headers
                ('query', (None, EventGQL.uploadMediaRawGQL())),
                ('variables', (None, variables)),
                ('theFiles', ("Duck.jpg", file, 'application/octet-stream'))
                ),
                headers={'Authorization': f'Bearer {self._mobilizon_client.loginTokens.accessToken}',
                         'accept': 'application/json'}
            )
        return response

    def logout(self):
        self._mobilizon_client.logOut()
        logger.info("Logged Out")
    
    def getActors(self):
        return self._mobilizon_client.publish(ActorsGQL.getIdentities())
    
    def getGroups(self):
        return self._mobilizon_client.publish(ActorsGQL.getGroups('"eventbot"'))

    # def update_event(self, actor_id, variables):
    # 	variables["organizerActorId"] = actor_id
    # 	return self._publish(UPDATE_GQL, variables)

    # def confirm_event(self, event_id):
    # 	variables = dict()
    # 	variables["eventId"] = event_id
    # 	return self._publish(CONFIRM_GQL, variables)

    # def cancel_event(self, event_id):
    # 	variables = dict()
    # 	variables["eventId"] = event_id
    # 	return self._publish(CANCEL_GQL, variables)

    # def delete_event(self, actor_id, event_id):
    # 	variables = { "actorId": actor_id,
    # 		"eventId" : event_id }
    # 	return self._publish(DELETE_GQL, variables)

    # # actors

    # def create_user(self, email, password):
    # 	variables = dict()
    # 	variables["email"] = email
    # 	variables["password"] = password
    # 	return self._publish(CREATE_USER_GQL, variables)

    # def create_person(self, name, preferredUsername, summary = ""):
    # 	variables = dict()
    # 	variables["name"] = name
    # 	variables["preferredUsername"] = preferredUsername
    # 	variables["summary"] = summary
    # 	return self._publish(CREATE_PERSON_GQL, variables)['createPerson']

    # def create_group(self, name, preferredUsername, summary = ""):
    # 	variables = dict()
    # 	variables["name"] = name
    # 	variables["preferredUsername"] = preferredUsername
    # 	variables["summary"] = summary
    # 	return self._publish(CREATE_GROUP_GQL, variables)['createGroup']

    # def create_member(self, group_id, preferredUsername):
    # 	variables = dict()
    # 	variables["groupId"] = group_id
    # 	variables["targetActorUsername"] = preferredUsername
    # 	return self._publish(CREATE_MEMBER_GQL, variables)['inviteMember']

    # def update_member(self, memberId, role):
    # 	variables = dict()
    # 	variables["memberId"] = memberId
    # 	variables["role"] = role
    # 	return self._publish(UPDATE_MEMBER_GQL, variables)['updateMember']

    # users / credentials

    # def user_identities(self):
    # 	variables = dict()
    # 	data = self._publish(PROFILES_GQL, variables)
    # 	profiles = data['identities']
    # 	return profiles

    # def user_memberships(self):
    # 	variables = { "limit": 20 }
    # 	data = self._publish(GROUPS_GQL, variables)
    # 	memberships = data['loggedUser']['memberships']['elements']
    # 	return memberships

    
