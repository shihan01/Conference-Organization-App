# Conference-Organization-App
Project 4 for Udacity Full-Stack Nanodegree


Set Up Instruction

1. Update the value of application in app.yaml to the app ID(testerproject-1154) in the App Engine admin console and would like to use to host your instance of this sample.

2. Update the values at the top of settings.py to reflect the respective client ID('791019144426-2rhiujd3jbu8d5l7pabnmsll9friqbf2.apps.googleusercontent.com')in the Developer Console.

3. Update the value of CLIENT_ID in static/js/app.js to the Web client ID'791019144426-2rhiujd3jbu8d5l7pabnmsll9friqbf2.apps.googleusercontent.com')

4. Run the app with the devserver using Google App Engine Laucher, and ensure it's running by visiting your local server's address (by default localhost:8080.)

5. Deploy your application.



----------------------------Task 1 design decisions------------------

Session

The session class has following fields:

name = ndb.StringProperty(required=True) - a string property representing the name of the session
highlights = ndb.StringProperty() - a text property (as highlights can be a longer text) representing the highlights of the session
speaker = ndb.StringProperty(repeated=True) - a string property (decided on having just a string property instead of a separate entity) representing the speakers of the session, and there could be multiple speakers
date = ndb.DateProperty() - a date property (converted in code from user input) representing the date of the session
start_time = ndb.TimeProperty() - a time property (converted in code from user input) representing the time of the session
duration = ndb.IntegerProperty() - an integer property (as it's a number with no need for decimal places) representing the duration of the session in minutes
type_of_session = ndb.StringProperty() - a string property (limited to the values of SessionType) representing the type of the session
location = ndb.StringProperty() - a string property (didn't want to use the location property as this is more the name of the room) representing the location of the session

I made Session decendants of profile, because it's easier for user to find all the sessions they add.
Also, all the sessions can be grouped by their 'confKey'.


Speaker

Speaker was not implemented as a separate entity, because I think the speaker don't need to sign up firstly. 

----------------------------Task 2 design decisions------------------

Storing of the wishlist

Wishlist is stored in a repeated string property (as it is websafeSessionKey) on the Profile.

Adding a session to the wishlist

Ideally the addSessionToWishlist would take a websafe key of the session,  but it will check whether the user has registered this conference.

Deleting a session to the wishlist

Ideally the addSessionToWishlist would remove a websafe key of the session,  but it will check whether the user has added this session.

--------------------------------Task 3 design decisions----------------

Two extra queries

I have added two additional queries.
The frist one is for the user to find all the sessions that has the same type in one location and order by name, because I think the user would like to know all the available sessions they interested

The second one is for the user ro find all the sessions that has the same speaker in one location and order by date. Since the user is interested in one speaker, I think the user is more interested in his or her schedule

Query problem

The problem with having query for both non-workshop and before 7pm sessions is that Google Datastore doesn't allow multiple inequalities for different properties. Possible solution would perfrom one inequality firstly, then perform second inequality when put them into `__copySessionToForm()`.
           @endpoints.method(message_types.VoidMessage, SessionForms,
                      path='filterSession3', http_method='GET', name='filterSession3')
           def filterSession3(self, request):
                """This is for the query problem in task 3"""
                #First inequality 
                s = Session.query(Session.startTime < time(19,0,0))
                return SessionForms(
                    #Second inequality
                    items=[self._copySessionToForm(sess) for sess in s if sess.typeOfSession!="workshop"]
                )

----------------------------Task 4 design decisions-----------------------

Featured speaker

Featured speaker is stored in memcache, and I mainly used task queue twice. 

When new session is being added, if it has a speaker, I will put all the info in task queue. This task queue will iterate through all sessions and find out whether there exists the speaker who has more than two sessions at that conference. If it does, put the 'key', 'speaker' and 'session name' into task queue. I use a dictionary structure to store all the featured speakers and their sessions.