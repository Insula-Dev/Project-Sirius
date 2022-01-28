# Imports
import json
import requests


# Local imports
from log_handling import *


# Variables
BASE_URL = "https://discordapp.com/api"
with open("token.txt") as file:
	HEADERS = {
		"Authorization": "Bot {}".format(file.read()),
		"Content-Type": "application/json"
	}


# API request decorator
def api_request(request):
	"""API request decorator.

	Looks out for bad responses, execute contingencies, document events in logs. Returns
	deserialized request text."""

	def wrapper(*args, **kwargs):

		r = request(*args, **kwargs)
		logger.debug("Request " + request.__name__ + " run with status code " + str(r.status_code))
		return json.loads(r.text)

	return wrapper


# API request functions
@api_request
def get_guild_audit_log(guild_id):
	"""GET/guilds/{guild.id}/audit-logs
	Returns an audit log object for the guild. Requires the 'VIEW_AUDIT_LOG' permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/audit-logs", headers=HEADERS)

@api_request
def get_channel(channel_id):
	"""GET/channels/{channel.id}
	Get a channel by ID. Returns a channel object. If the channel is a thread, a thread member
	object is included in the returned result."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id), headers=HEADERS)

@api_request
def modify_channel(channel_id):
	"""PATCH/channels/{channel.id}
	Update a channel's settings. Returns a channel on success, and a 400 BAD REQUEST on invalid
	parameters. All JSON parameters are optional."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/channels/" + str(channel_id), headers=HEADERS)

@api_request
def delete_close_channel(channel_id):
	"""DELETE/channels/{channel.id}
	Delete a channel, or close a private message. Requires the MANAGE_CHANNELS permission for the
	guild, or MANAGE_THREADS if the channel is a thread. Deleting a category does not delete its
	child channels; they will have their parent_id removed and a Channel Update Gateway event will
	fire for each of them. Returns a channel object on success. Fires a Channel Delete Gateway event
	(or Thread Delete if the channel was a thread)."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id), headers=HEADERS)

@api_request
def get_channel_messages(channel_id):
	"""GET/channels/{channel.id}/messages
	Returns the messages for a channel. If operating on a guild channel, this endpoint requires the
	VIEW_CHANNEL permission to be present on the current user. If the current user is missing the
	'READ_MESSAGE_HISTORY' permission in the channel then this will return no messages (since they
	cannot read the message history). Returns an array of message objects on success."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/messages", headers=HEADERS)

@api_request
def get_channel_message(channel_id, message_id):
	"""GET/channels/{channel.id}/messages/{message.id}
	Returns a specific message in the channel. If operating on a guild channel, this endpoint
	requires the 'READ_MESSAGE_HISTORY' permission to be present on the current user. Returns a
	message object on success."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id), headers=HEADERS)

@api_request
def create_message(channel_id, content, tts=False, embeds=None):
	"""POST/channels/{channel.id}/messages
	Post a message to a guild text or DM channel. Returns a message object. Fires a Message Create
	Gateway event. See message formatting for more information on how to properly format messages."""

	global BASE_URL, HEADERS

	request_body = {
		"content": content,
		"tts": tts,
		"embeds": embeds
	}

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/messages", headers=HEADERS, data=json.dumps(request_body))

@api_request
def crosspost_message(channel_id, message_id):
	"""POST/channels/{channel.id}/messages/{message.id}/crosspost
	Crosspost a message in a News Channel to following channels. This endpoint requires the
	'SEND_MESSAGES' permission, if the current user sent the message, or additionally the
	'MANAGE_MESSAGES' permission, for all other messages, to be present for the current user.
	Returns a message object."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/crosspost", headers=HEADERS)

@api_request
def create_reaction(channel_id, message_id, emoji):
	"""PUT/channels/{channel.id}/messages/{message.id}/reactions/{emoji}/@me
	Create a reaction for the message. This endpoint requires the 'READ_MESSAGE_HISTORY' permission
	to be present on the current user. Additionally, if nobody else has reacted to the message using
	this emoji, this endpoint requires the 'ADD_REACTIONS' permission to be present on the current
	user. Returns a 204 empty response on success. The emoji must be URL Encoded or the request will
	fail with 10014: Unknown Emoji. To use custom emoji, you must encode it in the format name:id
	with the emoji name and emoji id."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/reactions/" + str(emoji) + "/@me", headers=HEADERS)

@api_request
def delete_own_reaction(channel_id, message_id, emoji):
	"""DELETE/channels/{channel.id}/messages/{message.id}/reactions/{emoji}/@me
	Delete a reaction the current user has made for the message. Returns a 204 empty response on
	success. The emoji must be URL Encoded or the request will fail with 10014: Unknown Emoji. To
	use custom emoji, you must encode it in the format name:id with the emoji name and emoji id."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/reactions/" + str(emoji) + "/@me", headers=HEADERS)

@api_request
def delete_user_reaction(channel_id, message_id, emoji, user_id):
	"""DELETE/channels/{channel.id}/messages/{message.id}/reactions/{emoji}/{user.id}
	Deletes another user's reaction. This endpoint requires the 'MANAGE_MESSAGES' permission to be
	present on the current user. Returns a 204 empty response on success. The emoji must be URL
	Encoded or the request will fail with 10014: Unknown Emoji. To use custom emoji, you must encode
	it in the format name:id with the emoji name and emoji id."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/reactions/" + str(emoji) + "/" + str(user_id), headers=HEADERS)

@api_request
def get_reactions(channel_id, message_id, emoji):
	"""GET/channels/{channel.id}/messages/{message.id}/reactions/{emoji}
	Get a list of users that reacted with this emoji. Returns an array of user objects on success.
	The emoji must be URL Encoded or the request will fail with 10014: Unknown Emoji. To use custom
	emoji, you must encode it in the format name:id with the emoji name and emoji id."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/reactions/" + str(emoji), headers=HEADERS)

@api_request
def delete_all_reactions(channel_id, message_id):
	"""DELETE/channels/{channel.id}/messages/{message.id}/reactions
	Deletes all reactions on a message. This endpoint requires the 'MANAGE_MESSAGES' permission to
	be present on the current user. Fires a Message Reaction Remove All Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/reactions", headers=HEADERS)

@api_request
def delete_all_reactions_for_emoji(channel_id, message_id, emoji):
	"""DELETE/channels/{channel.id}/messages/{message.id}/reactions/{emoji}
	Deletes all the reactions for a given emoji on a message. This endpoint requires the
	MANAGE_MESSAGES permission to be present on the current user. Fires a Message Reaction Remove
	Emoji Gateway event. The emoji must be URL Encoded or the request will fail with 10014: Unknown
	Emoji. To use custom emoji, you must encode it in the format name:id with the emoji name and
	emoji id."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/reactions/" + str(emoji), headers=HEADERS)

@api_request
def edit_message(channel_id, message_id):
	"""PATCH/channels/{channel.id}/messages/{message.id}
	Edit a previously sent message. The fields content, embeds, and flags can be edited by the
	original message author. Other users can only edit flags and only if they have the
	MANAGE_MESSAGES permission in the corresponding channel. When specifying flags, ensure to
	include all previously set flags/bits in addition to ones that you are modifying. Only flags
	documented in the table below may be modified by users (unsupported flag changes are currently
	ignored without error). When the content field is edited, the mentions array in the message
	object will be reconstructed from scratch based on the new content. The allowed_mentions field
	of the edit request controls how this happens. If there is no explicit allowed_mentions in the
	edit request, the content will be parsed with default allowances, that is, without regard to
	whether or not an allowed_mentions was present in the request that originally created the
	message. Returns a message object. Fires a Message Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id), headers=HEADERS)

@api_request
def delete_message(channel_id, message_id):
	"""DELETE/channels/{channel.id}/messages/{message.id}
	Delete a message. If operating on a guild channel and trying to delete a message that was not
	sent by the current user, this endpoint requires the MANAGE_MESSAGES permission. Returns a 204
	empty response on success. Fires a Message Delete Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id), headers=HEADERS)

@api_request
def bulk_delete_messages(channel_id):
	"""POST/channels/{channel.id}/messages/bulk-delete
	Delete multiple messages in a single request. This endpoint can only be used on guild channels
	and requires the MANAGE_MESSAGES permission. Returns a 204 empty response on success. Fires a 
	Message Delete Bulk Gateway event. Any message IDs given that do not exist or are invalid will
	count towards the minimum and maximum message count (currently 2 and 100 respectively)."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + "bulk-delete", headers=HEADERS)

@api_request
def edit_channel_permissions(channel_id, overwrite_id):
	"""PUT/channels/{channel.id}/permissions/{overwrite.id}
	Edit the channel permission overwrites for a user or role in a channel. Only usable for guild
	channels. Requires the MANAGE_ROLES permission. Only permissions your bot has in the guild or
	channel can be allowed/denied (unless your bot has a MANAGE_ROLES overwrite in the channel).
	Returns a 204 empty response on success. For more information about permissions, see
	permissions."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/permissions/" + str(overwrite_id), headers=HEADERS)

@api_request
def get_channel_invites(channel_id):
	"""GET/channels/{channel.id}/invites
	Returns a list of invite objects (with invite metadata) for the channel. Only usable for guild
	channels. Requires the MANAGE_CHANNELS permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/invites", headers=HEADERS)

@api_request
def create_channel_invite(channel_id):
	"""POST/channels/{channel.id}/invites
	Create a new invite object for the channel. Only usable for guild channels. Requires the
	CREATE_INSTANT_INVITE permission. All JSON parameters for this route are optional, however the
	request body is not. If you are not sending any fields, you still have to send an empty JSON
	object ({}). Returns an invite object. Fires an Invite Create Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/invites", headers=HEADERS)

@api_request
def delete_channel_permission(channel_id, overwrite_id):
	"""DELETE/channels/{channel.id}/permissions/{overwrite.id}
	Delete a channel permission overwrite for a user or role in a channel. Only usable for guild
	channels. Requires the MANAGE_ROLES permission. Returns a 204 empty response on success. For
	more information about permissions, see permissions."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/permissions/" + str(overwrite_id), headers=HEADERS)

@api_request
def follow_news_channel(channel_id):
	"""POST/channels/{channel.id}/followers
	Follow a News Channel to send messages to a target channel. Requires the MANAGE_WEBHOOKS
	permission in the target channel. Returns a followed channel object."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/followers", headers=HEADERS)

@api_request
def trigger_typing_indicator(channel_id):
	"""POST/channels/{channel.id}/typing
	Post a typing indicator for the specified channel. Generally bots should not implement this
	route. However, if a bot is responding to a command and expects the computation to take a few
	seconds, this endpoint may be called to let the user know that the bot is processing their
	message. Returns a 204 empty response on success. Fires a Typing Start Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/typing", headers=HEADERS)

@api_request
def get_pinned_messages(channel_id):
	"""GET/channels/{channel.id}/pins
	Returns all pinned messages in the channel as an array of message objects."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/pins", headers=HEADERS)

@api_request
def pin_message(channel_id, message_id):
	"""PUT/channels/{channel.id}/pins/{message.id}
	Pin a message in a channel. Requires the MANAGE_MESSAGES permission. Returns a 204 empty
	response on success."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/pins/" + str(message_id), headers=HEADERS)

@api_request
def unpin_message(channel_id, message_id):
	"""DELETE/channels/{channel.id}/pins/{message.id}
	Unpin a message in a channel. Requires the MANAGE_MESSAGES permission. Returns a 204 empty
	response on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/pins/" + str(message_id), headers=HEADERS)

@api_request
def group_dm_add_recipient(channel_id, user_id):
	"""PUT/channels/{channel.id}/recipients/{user.id}
	Adds a recipient to a Group DM using their access token."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/recipients/" + str(user_id), headers=HEADERS)

@api_request
def group_dm_remove_recipient(channel_id, user_id):
	"""DELETE/channels/{channel.id}/recipients/{user.id}
	Removes a recipient from a Group DM."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/recipients/" + str(user_id), headers=HEADERS)

@api_request
def start_thread_with_message(channel_id, message_id):
	"""POST/channels/{channel.id}/messages/{message.id}/threads
	Creates a new thread from an existing message. Returns a channel on success, and a 400 BAD
	REQUEST on invalid parameters. Fires a Thread Create Gateway event. When called on a GUILD_TEXT
	channel, creates a GUILD_PUBLIC_THREAD. When called on a GUILD_NEWS channel, creates a
	GUILD_NEWS_THREAD. The id of the created thread will be the same as the id of the message, and
	as such a message can only have a single thread created from it."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/messages/" + str(message_id) + "/threads", headers=HEADERS)

@api_request
def start_thread_without_message(channel_id):
	"""POST/channels/{channel.id}/threads
	Creates a new thread that is not connected to an existing message. The created thread defaults
	to a GUILD_PRIVATE_THREAD. Returns a channel on success, and a 400 BAD REQUEST on invalid
	parameters. Fires a Thread Create Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/threads", headers=HEADERS)

@api_request
def join_thread(channel_id):
	"""PUT/channels/{channel.id}/thread-members/@me
	Adds the current user to a thread. Also requires the thread is not archived. Returns a 204 empty
	response on success. Fires a Thread Members Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/thread-members/@me", headers=HEADERS)

@api_request
def add_thread_member(channel_id, user_id):
	"""PUT/channels/{channel.id}/thread-members/{user.id}
	Adds another member to a thread. Requires the ability to send messages in the thread. Also
	requires the thread is not archived. Returns a 204 empty response on success. Fires a Thread
	Members Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/channels/" + str(channel_id) + "/thread-members/" + str(user_id), headers=HEADERS)

@api_request
def leave_thread(channel_id):
	"""DELETE/channels/{channel.id}/thread-members/@me
	Removes the current user from a thread. Also requires the thread is not archived. Returns a 204
	empty response on success. Fires a Thread Members Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/thread-members/@me", headers=HEADERS)

@api_request
def remove_thread_member(channel_id, user_id):
	"""DELETE/channels/{channel.id}/thread-members/{user.id}
	Removes another member from a thread. Requires the MANAGE_THREADS permission, or the creator of
	the thread if it is a GUILD_PRIVATE_THREAD. Also requires the thread is not archived. Returns a
	204 empty response on success. Fires a Thread Members Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/channels/" + str(channel_id) + "/thread-members/" + str(user_id), headers=HEADERS)

@api_request
def list_thread_members(channel_id):
	"""GET/channels/{channel.id}/thread-members
	Returns array of thread members objects that are members of the thread."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/thread-members", headers=HEADERS)

@api_request
def list_active_threads(channel_id):
	"""GET/channels/{channel.id}/threads/active
	Returns all active threads in the channel, including public and private threads. Threads are
	ordered by their id, in descending order."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/threads/active", headers=HEADERS)

@api_request
def list_public_archived_threads(channel_id):
	"""GET/channels/{channel.id}/threads/archived/public
	Returns archived threads in the channel that are public. When called on a GUILD_TEXT channel,
	returns threads of type GUILD_PUBLIC_THREAD. When called on a GUILD_NEWS channel returns threads
	of type GUILD_NEWS_THREAD. Threads are ordered by archive_timestamp, in descending order.
	Requires the READ_MESSAGE_HISTORY permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/threads/archived/public", headers=HEADERS)

@api_request
def list_private_archived_threads(channel_id):
	"""GET/channels/{channel.id}/threads/archived/private
	Returns archived threads in the channel that are of type GUILD_PRIVATE_THREAD. Threads are
	ordered by archive_timestamp, in descending order. Requires both the READ_MESSAGE_HISTORY and
	MANAGE_THREADS permissions."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/threads/archived/private", headers=HEADERS)

@api_request
def list_joined_private_archived_threads(channel_id):
	"""GET/channels/{channel.id}/users/@me/threads/archived/private
	Returns archived threads in the channel that are of type GUILD_PRIVATE_THREAD, and the user has
	joined. Threads are ordered by their id, in descending order. Requires the READ_MESSAGE_HISTORY
	permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/users/@me/threads/archived/private", headers=HEADERS)

@api_request
def list_guild_emojis(guild_id):
	"""GET/guilds/{guild.id}/emojis
	Returns a list of emoji objects for the given guild."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/emojis", headers=HEADERS)

@api_request
def get_guild_emoji(guild_id, emoji_id):
	"""GET/guilds/{guild.id}/emojis/{emoji.id}
	Returns an emoji object for the given guild and emoji IDs."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/emojis/" + str(emoji_id), headers=HEADERS)

@api_request
def create_guild_emoji(guild_id):
	"""POST/guilds/{guild.id}/emojis
	Create a new emoji for the guild. Requires the MANAGE_EMOJIS_AND_STICKERS permission. Returns
	the new emoji object on success. Fires a Guild Emojis Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/" + str(guild_id) + "/emojis", headers=HEADERS)

@api_request
def modify_guild_emoji(guild_id, emoji_id):
	"""PATCH/guilds/{guild.id}/emojis/{emoji.id}
	Modify the given emoji. Requires the MANAGE_EMOJIS_AND_STICKERS permission. Returns the updated
	emoji object on success. Fires a Guild Emojis Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/emojis/" + str(emoji_id), headers=HEADERS)

@api_request
def delete_guild_emoji(guild_id, emoji_id):
	"""DELETE/guilds/{guild.id}/emojis/{emoji.id}
	Delete the given emoji. Requires the MANAGE_EMOJIS_AND_STICKERS permission. Returns 204 No
	Content on success. Fires a Guild Emojis Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/emojis/" + str(emoji_id), headers=HEADERS)

@api_request
def create_guild():
	"""POST/guilds
	Create a new guild. Returns a guild object on success. Fires a Guild Create Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds", headers=HEADERS)

@api_request
def get_guild(guild_id):
	"""GET/guilds/{guild.id}
	Returns the guild object for the given id. If with_counts is set to true, this endpoint will
	also return approximate_member_count and approximate_presence_count for the guild."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id), headers=HEADERS)

@api_request
def get_guild_preview(guild_id):
	"""GET/guilds/{guild.id}/preview
	Returns the guild preview object for the given id. If the user is not in the guild, then the
	guild must be lurkable (it must be Discoverable or have a live public stage)."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/preview", headers=HEADERS)

@api_request
def modify_guild(guild_id):
	"""PATCH/guilds/{guild.id}
	Modify a guild's settings. Requires the MANAGE_GUILD permission. Returns the updated guild
	object on success. Fires a Guild Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id), headers=HEADERS)

@api_request
def delete_guild(guild_id):
	"""DELETE/guilds/{guild.id}
	Delete a guild permanently. User must be owner. Returns 204 No Content on success. Fires a Guild
	Delete Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id), headers=HEADERS)

@api_request
def get_guild_channels(guild_id):
	"""GET/guilds/{guild.id}/channels
	Returns a list of guild channel objects. Does not include threads."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/channels", headers=HEADERS)

@api_request
def create_guild_channel(guild_id):
	"""POST/guilds/{guild.id}/channels
	Create a new channel object for the guild. Requires the MANAGE_CHANNELS permission. If setting
	permission overwrites, only permissions your bot has in the guild can be allowed/denied. Setting
	MANAGE_ROLES permission in channels is only possible for guild administrators. Returns the new
	channel object on success. Fires a Channel Create Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/" + str(guild_id) + "/channels", headers=HEADERS)

@api_request
def modify_guild_channel_positions(guild_id):
	"""PATCH/guilds/{guild.id}/channels
	Modify the positions of a set of channel objects for the guild. Requires MANAGE_CHANNELS
	permission. Returns a 204 empty response on success. Fires multiple Channel Update Gateway
	events."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/channels", headers=HEADERS)

@api_request
def list_active_threads(guild_id):
	"""GET/guilds/{guild.id}/threads/active
	Returns all active threads in the guild, including public and private threads. Threads are
	ordered by their id, in descending order."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/threads/active", headers=HEADERS)

@api_request
def get_guild_member(guild_id, user_id):
	"""GET/guilds/{guild.id}/members/{user.id}
	Returns a guild member object for the specified user."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/members/" + str(user_id), headers=HEADERS)

@api_request
def list_guild_members(guild_id):
	"""GET/guilds/{guild.id}/members
	Returns a list of guild member objects that are members of the guild."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/members", headers=HEADERS)

@api_request
def search_guild_members(guild_id):
	"""GET/guilds/{guild.id}/members/search
	Returns a list of guild member objects whose username or nickname starts with a provided string."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/members/search", headers=HEADERS)

@api_request
def add_guild_member(guild_id, user_id):
	"""PUT/guilds/{guild.id}/members/{user.id}
	Adds a user to the guild, provided you have a valid oauth2 access token for the user with the
	guilds.join scope. Returns a 201 Created with the guild member as the body, or 204 No Content
	if the user is already a member of the guild. Fires a Guild Member Add Gateway event. For guilds
	with Membership Screening enabled, this endpoint will default to adding new members as pending
	in the guild member object. Members that are pending will have to complete membership screening 
	before they become full members that can talk."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/guilds/" + str(guild_id) + "/members/" + str(user_id), headers=HEADERS)

@api_request
def modify_guild_member(guild_id, user_id):
	"""PATCH/guilds/{guild.id}/members/{user.id}
	Modify attributes of a guild member. Returns a 200 OK with the guild member as the body. Fires a
	Guild Member Update Gateway event. If the channel_id is set to null, this will force the target
	user to be disconnected from voice."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/members/" + str(user_id), headers=HEADERS)

@api_request
def modify_current_user_nick(guild_id):
	"""PATCH/guilds/{guild.id}/members/@me/nick
	Modifies the nickname of the current user in a guild. Returns a 200 with the nickname on
	success. Fires a Guild Member Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/members/@me/nick", headers=HEADERS)

@api_request
def add_guild_member_role(guild_id, user_id, role_id):
	"""PUT/guilds/{guild.id}/members/{user.id}/roles/{role.id}
	Adds a role to a guild member. Requires the MANAGE_ROLES permission. Returns a 204 empty
	response on success. Fires a Guild Member Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/guilds/" + str(guild_id) + "/members/" + str(user_id) + "/roles/" + str(role_id), headers=HEADERS)

@api_request
def remove_guild_member_role(guild_id, user_id, role_id):
	"""DELETE/guilds/{guild.id}/members/{user.id}/roles/{role.id}
	Removes a role from a guild member. Requires the MANAGE_ROLES permission. Returns a 204 empty
	response on success. Fires a Guild Member Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/members/" + str(user_id) + "/roles/" + str(role_id), headers=HEADERS)

@api_request
def remove_guild_member(guild_id, user_id):
	"""DELETE/guilds/{guild.id}/members/{user.id}
	Remove a member from a guild. Requires KICK_MEMBERS permission. Returns a 204 empty response on
	success. Fires a Guild Member Remove Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/members/" + str(member_id), headers=HEADERS)

@api_request
def get_guild_bans(guild_id):
	"""GET/guilds/{guild.id}/bans
	Returns a list of ban objects for the users banned from this guild. Requires the BAN_MEMBERS
	permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/bans", headers=HEADERS)

@api_request
def get_guild_ban(guild_id, user_id):
	"""GET/guilds/{guild.id}/bans/{user.id}
	Returns a ban object for the given user or a 404 not found if the ban cannot be found. Requires
	the BAN_MEMBERS permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/bans/" + str(user_id), headers=HEADERS)

@api_request
def create_guild_ban(guild_id, user_id):
	"""PUT/guilds/{guild.id}/bans/{user.id}
	Create a guild ban, and optionally delete previous messages sent by the banned user. Requires
	the BAN_MEMBERS permission. Returns a 204 empty response on success. Fires a Guild Ban Add
	Gateway event."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/guilds/" + str(guild_id) + "/bans/" + str(user_id), headers=HEADERS)

@api_request
def remove_guild_ban(guild_id, user_id):
	"""DELETE/guilds/{guild.id}/bans/{user.id}
	Remove the ban for a user. Requires the BAN_MEMBERS permissions. Returns a 204 empty response on
	success. Fires a Guild Ban Remove Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/bans/" + str(user_id), headers=HEADERS)

@api_request
def get_guild_roles(guild_id):
	"""GET/guilds/{guild.id}/roles
	Returns a list of role objects for the guild."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/roles", headers=HEADERS)

@api_request
def create_guild_role(guild_id):
	"""POST/guilds/{guild.id}/roles
	Create a new role for the guild. Requires the MANAGE_ROLES permission. Returns the new role
	object on success. Fires a Guild Role Create Gateway event. All JSON params are optional."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/" + str(guild_id) + "/roles", headers=HEADERS)

@api_request
def modify_guild_role_positions(guild_id):
	"""PATCH/guilds/{guild.id}/roles
	Modify the positions of a set of role objects for the guild. Requires the MANAGE_ROLES
	permission. Returns a list of all of the guild's role objects on success. Fires multiple Guild
	Role Update Gateway events."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/roles", headers=HEADERS)

@api_request
def modify_guild_role(guild_id, role_id):
	"""PATCH/guilds/{guild.id}/roles/{role.id}
	Modify a guild role. Requires the MANAGE_ROLES permission. Returns the updated role on success.
	Fires a Guild Role Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/roles/" + str(role_id), headers=HEADERS)

@api_request
def delete_guild_role(guild_id):
	"""DELETE/guilds/{guild.id}/roles/{role.id}
	Delete a guild role. Requires the MANAGE_ROLES permission. Returns a 204 empty response on
	success. Fires a Guild Role Delete Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/roles/" + str(role_id), headers=HEADERS)

@api_request
def get_guild_prune_count(guild_id):
	"""GET/guilds/{guild.id}/prune
	Returns an object with one 'pruned' key indicating the number of members that would be removed
	in a prune operation. Requires the KICK_MEMBERS permission. By default, prune will not remove
	users with roles. You can optionally include specific roles in your prune by providing the
	include_roles parameter. Any inactive user that has a subset of the provided role(s) will be
	counted in the prune and users with additional roles will not."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/prune", headers=HEADERS)

@api_request
def begin_guild_prune(guild_id):
	"""POST/guilds/{guild.id}/prune
	Begin a prune operation. Requires the KICK_MEMBERS permission. Returns an object with one
	'pruned' key indicating the number of members that were removed in the prune operation. For
	large guilds it's recommended to set the compute_prune_count option to false, forcing 'pruned'
	to null. Fires multiple Guild Member Remove Gateway events. By default, prune will not remove
	users with roles. You can optionally include specific roles in your prune by providing the
	include_roles parameter. Any inactive user that has a subset of the provided role(s) will be 
	included in the prune and users with additional roles will not."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/" + str(guild_id) + "/prune", headers=HEADERS)

@api_request
def get_guild_voice_regions(guild_id):
	"""GET/guilds/{guild.id}/regions
	Returns a list of voice region objects for the guild. Unlike the similar /voice route, this
	returns VIP servers when the guild is VIP-enabled."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/regions", headers=HEADERS)

@api_request
def get_guild_invites(guild_id):
	"""GET/guilds/{guild.id}/invites
	Returns a list of invite objects (with invite metadata) for the guild. Requires the MANAGE_GUILD
	permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/invites", headers=HEADERS)

@api_request
def get_guild_integrations(guild_id):
	"""GET/guilds/{guild.id}/integrations
	Returns a list of integration objects for the guild. Requires the MANAGE_GUILD permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/integrations", headers=HEADERS)

@api_request
def delete_guild_integration(guild_id, integration_id):
	"""DELETE/guilds/{guild.id}/integrations/{integration.id}
	Delete the attached integration object for the guild. Deletes any associated webhooks and kicks
	the associated bot if there is one. Requires the MANAGE_GUILD permission. Returns a 204 empty 
	response on success. Fires a Guild Integrations Update Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/integrations/" + str(integration_id), headers=HEADERS)

@api_request
def get_guild_widget_setting(guild_id):
	"""GET/guilds/{guild.id}/widget
	Returns a guild widget object. Requires the MANAGE_GUILD permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/widget", headers=HEADERS)

@api_request
def modify_guild_widget(guild_id):
	"""PATCH/guilds/{guild.id}/widget
	Modify a guild widget object for the guild. All attributes may be passed in with JSON and
	modified. Requires the MANAGE_GUILD permission. Returns the updated guild widget object."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/widget", headers=HEADERS)

@api_request
def get_guild_widget(guild_id):
	"""GET/guilds/{guild.id}/widget.json
	Returns the widget for the guild."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/widget.json", headers=HEADERS)

@api_request
def get_guild_vanity_url(guild_id):
	"""GET/guilds/{guild.id}/vanity-url
	Returns a partial invite object for guilds with that feature enabled. Requires the MANAGE_GUILD
	permission. code will be null if a vanity url for the guild is not set."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/vanity-url", headers=HEADERS)

@api_request
def get_guild_widget_image(guild_id):
	"""GET/guilds/{guild.id}/widget.png
	Returns a PNG image widget for the guild. Requires no permissions or authentication."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/widget.png", headers=HEADERS)

@api_request
def get_guild_welcome_screen(guild_id):
	"""GET/guilds/{guild.id}/welcome-screen
	Returns the Welcome Screen object for the guild."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/welcome-screen", headers=HEADERS)

@api_request
def modify_guild_welcome_screen(guild_id):
	"""PATCH/guilds/{guild.id}/welcome-screen
	Modify the guild's Welcome Screen. Requires the MANAGE_GUILD permission. Returns the updated
	Welcome Screen object."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/welcome-screen", headers=HEADERS)

@api_request
def modify_current_user_voice_state(guild_id):
	"""PATCH/guilds/{guild.id}/voice-states/@me
	Updates the current user's voice state."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/voice-states/@me", headers=HEADERS)

@api_request
def modify_user_voice_state(guild_id, user_id):
	"""PATCH/guilds/{guild.id}/voice-states/{user.id}
	Updates another user's voice state."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/voice-states/" + str(user_id), headers=HEADERS)

@api_request
def get_guild_template(template_code):
	"""GET/guilds/templates/{template.code}
	Returns a guild template object for the given code."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/templates" + str(template_code), headers=HEADERS)

@api_request
def create_guild_from_guild_template(template_code):
	"""POST/guilds/templates/{template.code}
	Create a new guild based on a template. Returns a guild object on success. Fires a Guild Create
	Gateway event."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/templates/" + str(template_code), headers=HEADERS)

@api_request
def get_guild_templates(guild_id):
	"""GET/guilds/{guild.id}/templates
	Returns an array of guild template objects. Requires the MANAGE_GUILD permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/templates", headers=HEADERS)

@api_request
def create_guild_template(guild_id):
	"""POST/guilds/{guild.id}/templates
	Creates a template for the guild. Requires the MANAGE_GUILD permission. Returns the created
	guild template object on success."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/" + str(guild_id) + "/templates", headers=HEADERS)

@api_request
def sync_guild_template(guild_id, template_code):
	"""PUT/guilds/{guild.id}/templates/{template.code}
	Syncs the template to the guild's current state. Requires the MANAGE_GUILD permission. Returns
	the guild template object on success."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/guilds/" + str(guild_id) + "/templates/" + str(template_code), headers=HEADERS)

@api_request
def modify_guild_template(guild_id, template_code):
	"""PATCH/guilds/{guild.id}/templates/{template.code}
	Modifies the template's metadata. Requires the MANAGE_GUILD permission. Returns the guild
	template object on success."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/templates/" + str(template_code), headers=HEADERS)

@api_request
def delete_guild_template(guild_id, template_code):
	"""DELETE/guilds/{guild.id}/templates/{template.code}
	Deletes the template. Requires the MANAGE_GUILD permission. Returns the deleted guild template
	object on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/templates/" + str(template_code), headers=HEADERS)

@api_request
def get_invite(invite_code):
	"""GET/invites/{invite.code}
	Returns an invite object for the given code."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/invites/" + str(invite_code), headers=HEADERS)

@api_request
def delete_invite(invite_code):
	"""DELETE/invites/{invite.code}
	Delete an invite. Requires the MANAGE_CHANNELS permission on the channel this invite belongs to,
	or MANAGE_GUILD to remove any invite across the guild. Returns an invite object on success.
	Fires a Invite Delete Gateway event."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/invites/" + str(invite_code), headers=HEADERS)

@api_request
def create_stage_instance():
	"""POST/stage-instances
	Creates a new Stage instance associated to a Stage channel. Requires the user to be a moderator
	of the Stage channel."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/stage-instances", headers=HEADERS)

@api_request
def get_stage_instance(channel_id):
	"""GET/stage-instances/{channel.id}
	Gets the stage instance associated with the Stage channel, if it exists."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/stage-instances/" + str(channel_id), headers=HEADERS)

@api_request
def modify_stage_instance(channel_id):
	"""PATCH/stage-instances/{channel.id}
	Updates fields of an existing Stage instance. Requires the user to be a moderator of the Stage
	channel."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/stage-instances/" + str(channel_id), headers=HEADERS)

@api_request
def delete_stage_instance(channel_id):
	"""DELETE/stage-instances/{channel.id}
	Deletes the Stage instance. Requires the user to be a moderator of the Stage channel."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/stage-instances/" + str(channel_id), headers=HEADERS)

@api_request
def get_sticker(sticker_id):
	"""GET/stickers/{sticker.id}
	Returns a sticker object for the given sticker ID."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/stickers/" + str(sticker_id), headers=HEADERS)

@api_request
def list_nitro_sticker_packs():
	"""GET/sticker-packs
	Returns the list of sticker packs available to Nitro subscribers."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/sticker-packs/", headers=HEADERS)

@api_request
def list_guild_stickers(guild_id):
	"""GET/guilds/{guild.id}/stickers
	Returns an array of sticker objects for the given guild. Includes user fields if the bot has the
	MANAGE_EMOJIS_AND_STICKERS permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/stickers", headers=HEADERS)

@api_request
def get_guild_sticker(guild_id, sticker_id):
	"""GET/guilds/{guild.id}/stickers/{sticker.id}
	Returns a sticker object for the given guild and sticker IDs. Includes the user field if the bot
	has the MANAGE_EMOJIS_AND_STICKERS permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/stickers/" + str(sticker_id), headers=HEADERS)

@api_request
def create_guild_sticker(guild_id):
	"""POST/guilds/{guild.id}/stickers
	Create a new sticker for the guild. Send a multipart/form-data body. Requires the
	MANAGE_EMOJIS_AND_STICKERS permission. Returns the new sticker object on success."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/guilds/" + str(guild_id) + "/stickers", headers=HEADERS)

@api_request
def modify_guild_sticker(guild_id, sticker_id):
	"""PATCH/guilds/{guild.id}/stickers/{sticker.id}
	Modify the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission. Returns the
	updated sticker object on success."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/guilds/" + str(guild_id) + "/stickers/" + str(sticker_id), headers=HEADERS)

@api_request
def delete_guild_sticker(guild_id, sticker_id):
	"""DELETE/guilds/{guild.id}/stickers/{sticker.id}
	Delete the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission. Returns 204 No
	Content on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/guilds/" + str(guild_id) + "/stickers/" + str(sticker.id), headers=HEADERS)

@api_request
def get_current_user():
	"""GET/users/@me
	Returns the user object of the requester's account. For OAuth2, this requires the identify
	scope, which will return the object without an email, and optionally the email scope, which
	returns the object with an email."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/users/@me", headers=HEADERS)

@api_request
def get_user(user_id):
	"""GET/users/{user.id}
	Returns a user object for a given user ID."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/users/" + str(user_id), headers=HEADERS)

@api_request
def modify_current_user():
	"""PATCH/users/@me
	Modify the requester's user account settings. Returns a user object on success."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/users/@me", headers=HEADERS)

@api_request
def get_current_user_guilds():
	"""GET/users/@me/guilds
	Returns a list of partial guild objects the current user is a member of. Requires the guilds
	OAuth2 scope."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/users/@me/guilds", headers=HEADERS)

@api_request
def leave_guild(user_id):
	"""DELETE/users/@me/guilds/{guild.id}
	Leave a guild. Returns a 204 empty response on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/users/@me/guilds/" + str(user_id), headers=HEADERS)

@api_request
def create_dm():
	"""POST/users/@me/channels
	Create a new DM channel with a user. Returns a DM channel object."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/users/@me/channels", headers=HEADERS)

@api_request
def create_group_dm():
	"""POST/users/@me/channels
	Create a new group DM channel with multiple users. Returns a DM channel object. This endpoint
	was intended to be used with the now-deprecated GameBridge SDK. DMs created with this endpoint
	will not be shown in the Discord client."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/users/@me/channels", headers=HEADERS)

@api_request
def get_user_connections():
	"""GET/users/@me/connections
	Returns a list of connection objects. Requires the connections OAuth2 scope."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/users/@me/connections", headers=HEADERS)

@api_request
def list_voice_regions():
	"""GET/voice/regions
	Returns an array of voice region objects that can be used when setting a voice or stage
	channel's rtc_region."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/voice/regions", headers=HEADERS)

@api_request
def create_webhook(channel_id):
	"""POST/channels/{channel.id}/webhooks
	Create a new webhook. Requires the MANAGE_WEBHOOKS permission. Returns a webhook object on
	success. Webhook names follow our naming restrictions that can be found in our Usernames and
	Nicknames documentation, with the following additional stipulations:
		Webhook names cannot be: 'clyde'"""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/channels/" + str(channel_id) + "/webhooks", headers=HEADERS)

@api_request
def get_channel_webhooks(channel_id):
	"""GET/channels/{channel.id}/webhooks
	Returns a list of channel webhook objects. Requires the MANAGE_WEBHOOKS permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/channels/" + str(channel_id) + "/webhooks", headers=HEADERS)

@api_request
def get_guild_webhooks(guild_id):
	"""GET/guilds/{guild.id}/webhooks
	Returns a list of guild webhook objects. Requires the MANAGE_WEBHOOKS permission."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/guilds/" + str(guild_id) + "/webhooks", headers=HEADERS)

@api_request
def get_webhook(webhook_id):
	"""GET/webhooks/{webhook.id}
	Returns the new webhook object for the given id."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/webhooks/" + str(webhook_id), headers=HEADERS)

@api_request
def get_webhook_with_token(webhook_id, webhook_token):
	"""GET/webhooks/{webhook.id}/{webhook.token}
	Same as above, except this call does not require authentication and returns no user in the
	webhook object."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token), headers=HEADERS)

@api_request
def modify_webhook(webhook_id):
	"""PATCH/webhooks/{webhook.id}
	Modify a webhook. Requires the MANAGE_WEBHOOKS permission. Returns the updated webhook object on
	success."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/webhooks/" + str(webhook_id), headers=HEADERS)

@api_request
def modify_webhook_with_token(webhook_id, webhook_token):
	"""PATCH/webhooks/{webhook.id}/{webhook.token}
	Same as above, except this call does not require authentication, does not accept a channel_id
	parameter in the body, and does not return a user in the webhook object."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token), headers=HEADERS)

@api_request
def delete_webhook(webhook_id):
	"""DELETE/webhooks/{webhook.id}
	Delete a webhook permanently. Requires the MANAGE_WEBHOOKS permission. Returns a 204 NO CONTENT
	response on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/webhooks/" + str(webhook_id), headers=HEADERS)

@api_request
def delete_webhook_with_token(webhook_id, webhook_token):
	"""DELETE/webhooks/{webhook.id}/{webhook.token}
	Same as above, except this call does not require authentication."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token), headers=HEADERS)

@api_request
def execute_webhook(webhook_id, webhook_token):
	"""POST/webhooks/{webhook.id}/{webhook.token}"""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token), headers=HEADERS)

@api_request
def execute_slack_compatible_webhook(webhook_id, webhook_token):
	"""POST/webhooks/{webhook.id}/{webhook.token}/slack
	Refer to Slack's documentation for more information. We do not support Slack's channel,
	icon_emoji, mrkdwn, or mrkdwn_in properties."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token) + "/slack", headers=HEADERS)

@api_request
def execute_github_compatible_webhook(webhook_id):
	"""POST/webhooks/{webhook.id}/{webhook.token}/github
	Add a new webhook to your GitHub repo (in the repo's settings), and use this endpoint as the
	"Payload URL." You can choose what events your Discord channel receives by choosing the "Let me
	select individual events" option and selecting individual events for the new webhook you're
	configuring."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token) + "/github", headers=HEADERS)

@api_request
def get_webhook_message(webhook_id, webhook_token, message_id):
	"""GET/webhooks/{webhook.id}/{webhook.token}/messages/{message.id}
	Returns a previously-sent webhook message from the same token. Returns a message object on
	success."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token) + "/messages/" + str(message_id), headers=HEADERS)

@api_request
def edit_webhook_message(webhook_id, webhook_token, message_id):
	"""PATCH/webhooks/{webhook.id}/{webhook.token}/messages/{message.id}
	Edits a previously-sent webhook message from the same token. Returns a message object on
	success. When the content field is edited, the mentions array in the message object will be
	reconstructed from scratch based on the new content. The allowed_mentions field of the edit
	request controls how this happens. If there is no explicit allowed_mentions in the edit request,
	the content will be parsed with default allowances, that is, without regard to whether or not an
	allowed_mentions was present in the request that originally created the message."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token) + "/messages/" + str(message_id), headers=HEADERS)

@api_request
def delete_webhook_message(webhook_id, webhook_token, message_id):
	"""DELETE/webhooks/{webhook.id}/{webhook.token}/messages/{message.id}
	Deletes a message that was created by the webhook. Returns a 204 NO CONTENT response on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/webhooks/" + str(webhook_id) + "/" + str(webhook_token) + "/messages/" + str(message_id), headers=HEADERS)

@api_request
def get_current_bot_application_information():
	"""GET/oauth2/applications/@me
	Returns the bot's application object."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/oauth2/applications/@me", headers=HEADERS)

@api_request
def get_current_authorization_information():
	"""GET/oauth2/@me
	Returns info about the current authorization. Requires authentication with a bearer token."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/oauth2/@me", headers=HEADERS)


# Interactions - Application command functions
@api_request
def get_global_application_commands(application_id):
	"""GET/applications/{application.id}/commands
	Fetch all of the global commands for your application. Returns an array of application command objects."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/applications/" + application_id + "/commands", headers=HEADERS)

@api_request
def create_global_application_command(application_id):
	"""POST/applications/{application.id}/commands
	Create a new global command. New global commands will be available in all guilds after 1 hour. Returns 201 and an application command object."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/applications/" + application_id + "/commands", headers=HEADERS)

@api_request
def get_global_command_application(application_id, command_id):
	"""GET/applications/{application.id}/commands/{command.id}
	Fetch a global command for your application. Returns an application command object."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/applications/" + application_id + "/commands/" + command_id, headers=HEADERS)

@api_request
def edit_global_application_command(application_id, command_id):
	"""PATCH/applications/{application.id}/commands/{command.id}
	Edit a global command. Updates will be available in all guilds after 1 hour. Returns 200 and an application command object."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/applications/" + application_id + "/commands/" + command_id, headers=HEADERS)

@api_request
def delete_global_application_command(application_id, command_id):
	"""DELETE/applications/{application.id}/commands/{command.id}
	Deletes a global command. Returns 204 No Content on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/applications/"+ application_id + "/commands/" + command_id, headers=HEADERS)

@api_request
def bulk_overwrite_global_application_commands(application_id):
	"""PUT/applications/{application.id}/commands
	Takes a list of application commands, overwriting the existing global command list for this application. Updates will be available in all guilds after 1 hour. Returns 200 and a list of application command objects. Commands that do not already exist will count toward daily application command create limits."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/applications/" + application_id + "/commands", headers=HEADERS)

@api_request
def get_guild_application_commands(application_id, guild_id):
	"""GET/applications/{application.id}/guilds/{guild.id}/commands
	Fetch all of the guild commands for your application for a specific guild. Returns an array of application command objects."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands", headers=HEADERS)

@api_request
def create_guild_application_command(application_id, guild_id):
	"""POST/applications/{application.id}/guilds/{guild.id}/commands
	Create a new guild command. New guild commands will be available in the guild immediately. Returns 201 and an application command object. If the command did not already exist, it will count toward daily application command create limits."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands", headers=HEADERS)

@api_request
def get_guild_application_command(application_id, guild_id, command_id):
	"""GET/applications/{application.id}/guilds/{guild.id}/commands/{command.id}
	Fetch a guild command for your application. Returns an application command object."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/" + command_id, headers=HEADERS)

@api_request
def edit_guild_application_command(application_id, guild_id, command_id):
	"""PATCH/applications/{application.id}/guilds/{guild.id}/commands/{command.id}
	Edit a guild command. Updates for guild commands will be available immediately. Returns 200 and an application command object."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/" + command_id, headers=HEADERS)

@api_request
def delete_guild_application_command(application_id, guild_id, command_id):
	"""DELETE/applications/{application.id}/guilds/{guild.id}/commands/{command.id}
	Delete a guild command. Returns 204 No Content on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/" + command_id, headers=HEADERS)

@api_request
def bulk_overwrite_guild_application_commands(application_id, guild_id):
	"""PUT/applications/{application.id}/guilds/{guild.id}/commands
	Takes a list of application commands, overwriting the existing command list for this application for the targeted guild. Returns 200 and a list of application command objects."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands", headers=HEADERS)

@api_request
def get_guild_application_command_permissions(application_id, guild_id):
	"""GET/applications/{application.id}/guilds/{guild.id}/commands/permissions
	Fetches command permissions for all commands for your application in a guild. Returns an array of guild application command permissions objects."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/permissions", headers=HEADERS)

@api_request
def get_application_command_permissions(application_id, guild_id, command_id):
	"""GET/applications/{application.id}/guilds/{guild.id}/commands/{command.id}/permissions
	Fetches command permissions for a specific command for your application in a guild. Returns a guild application command permissions object."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/" + command_id + "/permissions", headers=HEADERS)

@api_request
def edit_application_command_permissions(application_id, guild_id, command_id):
	"""PUT/applications/{application.id}/guilds/{guild.id}/commands/{command.id}/permissions
	Edits command permissions for a specific command for your application in a guild. You can only add up to 10 permission overwrites for a command. Returns a GuildApplicationCommandPermissions object."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/" + command_id + "/permissions", headers=HEADERS)

@api_request
def batch_edit_application_command_permissions(application_id, guild_id):
	"""PUT/applications/{application.id}/guilds/{guild.id}/commands/permissions
	Batch edits permissions for all commands in a guild. Takes an array of partial guild application command permissions objects including id and permissions.
	You can only add up to 10 permission overwrites for a command.
	Returns an array of GuildApplicationCommandPermissions objects."""

	global BASE_URL, HEADERS

	return requests.put(BASE_URL + "/applications/" + application_id + "/guilds/" + guild_id + "/commands/permissions", headers=HEADERS)


# Interactions - Receiving and responding functions
@api_request
def create_interaction_response(interaction_id, interaction_token):
	"""POST/interactions/{interaction.id}/{interaction.token}/callback
	Create a response to an Interaction from the gateway. Takes an interaction response. This endpoint also supports file attachments similar to the webhook endpoints. Refer to Uploading Files for details on uploading files and multipart/form-data requests.
"""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/interactions/" + interaction_id + "/" + interaction_token + "/callback", headers=HEADERS)

@api_request
def get_original_interaction_response(application_id, interaction_token):
	"""GET/webhooks/{application.id}/{interaction.token}/messages/@original
	Returns the initial Interaction response. Functions the same as Get Webhook Message."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token + "/messages/@original", headers=HEADERS)

@api_request
def edit_original_interaction_response(application_id, interaction_token):
	"""PATCH/webhooks/{application.id}/{interaction.token}/messages/@original
	Edits the initial Interaction response. Functions the same as Edit Webhook Message."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token + "/messages/@original", headers=HEADERS)

@api_request
def delete_original_interaction_response(application_id, interaction_token):
	"""DELETE/webhooks/{application.id}/{interaction.token}/messages/@original
	Deletes the initial Interaction response. Returns 204 No Content on success."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token + "/messages/@original", headers=HEADERS)

@api_request
def create_followup_message(application_id, interaction_token):
	"""POST/webhooks/{application.id}/{interaction.token}
	Create a followup message for an Interaction. Functions the same as Execute Webhook, but wait is always true, and flags can be set to 64 in the body to send an ephemeral message. The thread_id, avatar_url, and username parameters are not supported when using this endpoint for interaction followups."""

	global BASE_URL, HEADERS

	return requests.post(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token, headers=HEADERS)

@api_request
def get_followup_message(application_id, interaction_token, message_id):
	"""GET/webhooks/{application.id}/{interaction.token}/messages/{message.id}
	Returns a followup message for an Interaction. Functions the same as Get Webhook Message. Does not support ephemeral followups."""

	global BASE_URL, HEADERS

	return requests.get(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token + "/messages/" + message.id, headers=HEADERS)

@api_request
def edit_followup_message(application_id, interaction_token, message_id):
	"""PATCH/webhooks/{application.id}/{interaction.token}/messages/{message.id}
	Edits a followup message for an Interaction. Functions the same as Edit Webhook Message. Does not support ephemeral followups."""

	global BASE_URL, HEADERS

	return requests.patch(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token + "/messages/" + message_id, headers=HEADERS)

@api_request
def delete_followup_message(application_id, interaction_token, message_id):
	"""DELETE/webhooks/{application.id}/{interaction.token}/messages/{message.id}
	Deletes a followup message for an Interaction. Returns 204 No Content on success. Does not support ephemeral followups."""

	global BASE_URL, HEADERS

	return requests.delete(BASE_URL + "/webhooks/" + application_id + "/" + interaction_token + "/messages/" + message_id, headers=HEADERS)


# Main code
if __name__ == "__main__":

	# Add your code here, and don't commit changes to this file
	pass
