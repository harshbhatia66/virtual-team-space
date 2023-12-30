### Branch Management
With our branch management, we as a team decided to created a develop branch that will act as our master branch. We have first branched out to different features and have first implemented the testings for all features and merged to the develop branch, so that as a team we collaboratively assess all the testings. After that we then implement these functions on our seperate branches and to use pytest on our individual functions eg. pytest tests/auth_register_test.py to test the validity of a successful pipeline of the particular function to merge to develop as we are aware it will be a 'failed pipeline' as all other testings have not been implemented'. We do this to identify, big picture bugs that could posssibly occur when merging with other branches by the time we finish all our implementation the pipeline should then be successful.

### channels_create
In src/channels.py for def channels_create_v1(auth_user_id, name, is_public):
Assuming that the auth_user_id is correct and is within in the database

In tests/channels_create_test.py and channels_create_v1.py:
Assuming that users have been created successfully.
Assuming that there can't be duplicate channel names 

### channels_list and listall
In tests/channels_listall_test.py and tests/channels_list_test.py:
Assuming that entering an invalid token/token with invalid auth_user_id will still raise access errors.

### channel_messages
In tests/channel_messages_test.py:
Assuming that when there is an empty array of messages, the end value will technically have no more messsages to load and therefore it will return -1.

# tokens.py and unique_id.py
- tokens.py contains helper functions to generate tokens and encrypt passwords
- these files has also been added to .coveragerc as these are just helper classes and functions to generate outputs