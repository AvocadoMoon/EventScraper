from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from requests.exceptions import HTTPError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from drivers.mobilizon.gql_requests import EventGQL, AuthenticationGQL
from drivers.mobilizon.mobilizon_types import EventType


def _build_client(endpoint, bearer=None):
    headers = dict()
    if bearer is not None:
        headers['Authorization'] = 'Bearer ' + bearer
    transport = RequestsHTTPTransport(
        url=endpoint,
        headers=headers,
        verify=True,
        # retries=3,
    )
    return Client(transport=transport, fetch_schema_from_transport=True)


class retry_if_not_exception_type(retry_if_exception):
    """Retries except an exception has been raised of one or more types."""

    def __init__(self, exception_types=Exception):
        self.exception_types = exception_types
        super(retry_if_not_exception_type, self).__init__(
            lambda e: not isinstance(e, exception_types))


class BadRequest(Exception):
    pass


class Mobilizon:
    loginTokens: [] = None
    client = None

    def __init__(self, endpoint: str, email: str, password: str):
        self.loginTokens = self._login(endpoint, email, password)

    # events

    def create_event(self, eventInfo: EventType):
        return self._publish(EventGQL.createEventGQL(eventInfo))

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

    def logout(self):
        return self._publish(AuthenticationGQL.logoutGQL(f'"{self.loginTokens[1]}"'))  # void

    def refresh_token(self, refreshToken: str):
        return self._publish(AuthenticationGQL.refreshTokenGQL(refreshToken))

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

    def _login(self, endpoint, email: str, password: str):
        self.client = _build_client(endpoint)
        data = self._publish(AuthenticationGQL.loginGQL(email, password))
        login = data['login']
        self.client = _build_client(endpoint, login['accessToken'])
        return login['accessToken'], login['refreshToken']

    # attempts at 0s, 2s, 4s, 8s
    @retry(reraise=True, retry=retry_if_not_exception_type(BadRequest), stop=stop_after_attempt(4),
           wait=wait_exponential(multiplier=2))
    def _publish(self, query):
        try:
            response = self.client.execute(query)
        except HTTPError as e:
            if e.response.status_code in [400, 404]:
                raise BadRequest(e)
            else:
                raise
        except TransportQueryError as e:
            raise BadRequest(e)
        except:
            raise
        return response
