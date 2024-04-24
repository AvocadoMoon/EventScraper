import gql
# https://github.com/framasoft/mobilizon/blob/main/docs/dev.md

# ==== GQL : Events ====
class EventGQL:
  def createEventGQL(eventInformation: EventType):
    gqlString = f"""
    mutation createEvent {{
      organizerActorId: {eventInformation.organizerActorId}, 
      attributedToId: {eventInformation.attributedToId}, 
      title: {eventInformation.title}, 
      description: {eventInformation.description}, 
      beginsOn: {eventInformation.beginsOn}, 
      endsOn: {eventInformation.endsOn}, 
      status: {eventInformation.status}, 
      visibility: {eventInformation.visibility}, 
      joinOptions: {eventInformation.joinOptions}, 
      draft: {eventInformation.draft}, 
      tags: {eventInformation.tags},
      picture: {eventInformation.picture}, 
      onlineAddress: {eventInformation.onlineAddress}, 
      phoneAddress: {eventInformation.phoneAddress}, 
      category: {eventInformation.category}, 
      physicalAddress: {eventInformation.physicalAddress}, 
      options: {eventInformation.options}, 
      contacts: {eventInformation.contacts}
      {{
        id
        uuid
      }}
    }}
    """
    return gql(gqlString)

  


# ==== GQL : credentials ====

class AuthenticationGQL:
  def loginGQL(email, password):
    gqlString = f"""
      mutation login {{
      email: {email}, 
      password: {password} {{
        accessToken   
        refreshToken
      }}
    }}
    """
    return gql(gqlString)
  
  def logoutGQL(refreshToken):
    gqlString = f"""
      mutation logout {{
      refreshToken: {refreshToken}
    }}
    """
    return gql(gqlString)
  
  def refreshTokenGQL(refreshToken):
    gqlString = f"""
      mutation RefreshToken {{
      refreshToken: {refreshToken} {{
	    accessToken   
      refreshToken
      }}
    }}"""
    return gql(gqlString)


# UPDATE_GQL = gql("""
# mutation updateEvent($id: ID!, $title: String, $description: String, $beginsOn: DateTime, $endsOn: DateTime, $status: EventStatus, $visibility: EventVisibility, $joinOptions: EventJoinOptions, $draft: Boolean, $tags: [String], $picture: PictureInput, $onlineAddress: String, $phoneAddress: String, $organizerActorId: ID, $attributedToId: ID, $category: String, $physicalAddress: AddressInput, $options: EventOptionsInput, $contacts: [Contact]) {
#   updateEvent(eventId: $id, title: $title, description: $description, beginsOn: $beginsOn, endsOn: $endsOn, status: $status, visibility: $visibility, joinOptions: $joinOptions, draft: $draft, tags: $tags, picture: $picture, onlineAddress: $onlineAddress, phoneAddress: $phoneAddress, organizerActorId: $organizerActorId, attributedToId: $attributedToId, category: $category, physicalAddress: $physicalAddress, options: $options, contacts: $contacts) {
# 	id
# 	uuid
#   }
# }
# """)


# CANCEL_GQL = gql("""
# mutation updateEvent($eventId: ID!) {
#   updateEvent(eventId: $eventId, status: CANCELLED) {
# 	id
# 	uuid
#   }
# }
# """)

# CONFIRM_GQL = gql("""
# mutation updateEvent($eventId: ID!) {
#   updateEvent(eventId: $eventId, status: CONFIRMED) {
# 	id
# 	uuid
#   }
# }
# """)


# DELETE_GQL = gql("""
# mutation DeleteEvent($eventId: ID!) {
#   deleteEvent(eventId: $eventId) {
# 	id
#   }
# }
# """)

# # ==== /GQL : Events ====

# # ==== GQL : Actors ====

# CREATE_USER_GQL = gql("""
# mutation createUser($email: String!, $locale: String="fr", $password: String!) {
#   createUser(email: $email, locale: $locale, password: $password) {
# 	id
#   }
# }""")

# CREATE_GROUP_GQL = gql("""
# mutation createGroup($name: String, $preferredUsername: String!, $summary: String = "") {
#   createGroup(name: $name, preferredUsername: $preferredUsername, summary: $summary) {
# 	id
#   }
# }""")

# CREATE_PERSON_GQL = gql("""
# mutation createPerson($name: String, $preferredUsername: String!, $summary: String = "") {
#   createPerson(name: $name, preferredUsername: $preferredUsername, summary: $summary) {
# 	id   url
#   }
# }""")

# CREATE_MEMBER_GQL = gql("""
# mutation inviteMember($groupId: ID!, $targetActorUsername: String!) {
#   inviteMember(groupId: $groupId, targetActorUsername: $targetActorUsername) {
# 	id   role
#   }
# }""")

# UPDATE_MEMBER_GQL = gql("""
# mutation updateMemberRole($memberId: ID!, $role:MemberRoleEnum!) {
#   updateMember(memberId: $memberId, role: $role) {
# 	id   role
#   }
# }""")

# # ==== /GQL : Users ====

# # ==== /GQL : credentials ====

# # ==== GQL : identities - actors - persons and groups ====

# PROFILES_GQL = gql("""
# query Identities { identities { ...ActorFragment } }
# fragment ActorFragment on Actor { id type preferredUsername name url}
# """)

# GROUPS_GQL = gql("""
# query LoggedUserMemberships($membershipName: String, $page: Int, $limit: Int) {
#   loggedUser {
# 	memberships(name: $membershipName, page: $page, limit: $limit) {
# 	  elements {
# 		role
# 		actor { ...ActorFragment }
# 		parent { ...ActorFragment }
# 	  }
# 	}     
#   }
# }
# fragment ActorFragment on Actor {  id type  preferredUsername  name }
# """)
