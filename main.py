#!/usr/bin/env python

"""
main.py -- Udacity conference server-side Python App Engine
    HTTP controller handlers for memcache & task queue access

$Id$

created by wesc on 2014 may 24

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from conference import ConferenceApi
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from models import Session

class SetAnnouncementHandler(webapp2.RequestHandler):
    def get(self):
        """Set Announcement in Memcache."""
        ConferenceApi._cacheAnnouncement()
        self.response.set_status(204)


class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email confirming Conference creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Conference!',            # subj
            'Hi, you have created a following '         # body
            'conference:\r\n\r\n%s' % self.request.get(
                'conferenceInfo')
        )
class CheckFeaturedSpeaker(webapp2.RequestHandler):
    def post(self):
        MEMCACHE_FEATURED_SPEAKERS_KEY = "FEATURED SPEAKERS"
        speaker = self.request.get('current_speaker')
        sessions = Session.query(Session.speaker == speaker)
        for session in sessions:
            #Make sure all the sessions are under the same conference,
            #and excluding the current session itself, cause the current session may be
            #already in the database
            if getattr(session, 'confKey') == self.request.get('current_confKey') and \
            session.key.urlsafe() != self.request.get('current_websafeKey'):
                val = memcache.get(MEMCACHE_FEATURED_SPEAKERS_KEY)
                #The first time that the speaker is a featured speaker, put the speaker and 
                #two sessions under the speaker
                if not val or speaker not in val:
                    taskqueue.add(params={'val': self.request.get('current_name'),
                                          'speaker': speaker,
                                      'MEMCACHE_FEATURED_SPEAKERS_KEY': MEMCACHE_FEATURED_SPEAKERS_KEY},
                                       url='/sessions/addFeaturedSpeaker')
                    taskqueue.add(params={'val': getattr(session,'name'),
                                          'speaker':speaker,
                                      'MEMCACHE_FEATURED_SPEAKERS_KEY': MEMCACHE_FEATURED_SPEAKERS_KEY},
                                       url='/sessions/addFeaturedSpeaker')
                #The speaker is already a featured speaker, just need to add session name under the speaker
                else:
                    taskqueue.add(params={'val': self.request.get('current_name'),
                                          'speaker':speaker,
                                      'MEMCACHE_FEATURED_SPEAKERS_KEY': MEMCACHE_FEATURED_SPEAKERS_KEY},
                                       url='/sessions/addFeaturedSpeaker')
                #Avoid adding same sessions again and again
                break

class AddSpeakerToMemecacheHandler(webapp2.RequestHandler):
    def post(self):
        """Add Featured speaker to memcache"""
        speaker =self.request.get("speaker")
        featuredSpeakers = memcache.get(self.request.get('MEMCACHE_FEATURED_SPEAKERS_KEY'))
        if not featuredSpeakers:
            featuredSpeakers={} 
        if speaker in featuredSpeakers:
            featuredSpeakers[speaker].append(self.request.get('val'))
        else:
            featuredSpeakers[speaker] = [self.request.get('val')]
        memcache.set(self.request.get('MEMCACHE_FEATURED_SPEAKERS_KEY'), featuredSpeakers)
        
        


app = webapp2.WSGIApplication([
    ('/crons/set_announcement', SetAnnouncementHandler),
    ('/tasks/send_confirmation_email', SendConfirmationEmailHandler),
    ('/sessions/checkFeaturedSpeaker', CheckFeaturedSpeaker),
    ('/sessions/addFeaturedSpeaker', AddSpeakerToMemecacheHandler)
], debug=True)
