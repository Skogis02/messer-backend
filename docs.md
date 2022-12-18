
## Base Message to Server

    {
        "endpoint": str,
        "id"?: str,
        "content": {
            ...
        }
    }

Generic Errors:

?0: Invalid JSON
?1: Serialization Error

## Endpoints:

### "send_message"

    "content": {
        "friend": str,
        "content": str
    }
    
Error prefix: "1"

Errors:

12: Friend not found.

### "send_friend_request"

    "content": {
        "to_user": str
    }

Error prefix: "2"

Errors:

22: User not found.
23: User is friend.
24: Already friends.
25: Friend request already sent.
26: Unknown Error.

### "respond_to_friend_request"

    "content": {
        "from_user": str,
        "accept": bool
    }

Error prefix: "3"

Errors:

32: No friend request received.

### "withdraw_friend_request"

    "content": {
        "to_user": str
    }

Error prefix: "4"

Errors:

42: No friend request received.

### "remove_friend"

    "content": {
        "friend": str
    }

Error prefic: "5"

Errors:

52: Friend not found

### "get_friends":

    "content": {}

### "get_messages"

    "content": {}

### "get_friend_requests"

    "content": {}
