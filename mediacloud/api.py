
import json
import requests
import re

class MediaCloud(object):
    '''
    Simple client library for the nascent MediaCloud story feed API
    '''

    VERSION = "0.2"

    OLD_API_URL = "http://amanda.law.harvard.edu/admin/stories/"
    API_URL = "http://amanda.law.harvard.edu/admin/api/stories/"

    DEFAULT_STORY_COUNT = 25

    def __init__(self, api_user=None, api_pass=None):
        self._api_user = api_user
        self._api_pass = api_pass
        
    def createStorySubset(self, start_date, end_date, media_id):
        '''
        Call this to create a subset of stories by date and media source.  This will return a subset id.
        Call this once, then use isStorySubsetReady to check if it is ready.
        It will take the backend system a while to generate the stream of stories for the newly created subset.
        Date format is YYYY-MM-DD
        '''
        date_format = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
        if not date_format.match(start_date):
            raise ValueError('start_date must be in YYYY-MM-DD')
        if not date_format.match(end_date):
            raise ValueError('start_date must be in YYYY-MM-DD')
        params = {'media_id':media_id, 'end_date':end_date, 'start_date':start_date}
        results = self._query('subset/', {'data':json.dumps(params,separators=(',',':'))} )
        return results['story_subsets_id']

    def storySubsetDetail(self, subset_id):
        '''
        '''
        return self._query('subset/'+str(subset_id), {}, 'GET')

    def isStorySubsetReady(self, subset_id):
        '''
        Checks if a story subset is complete.  This can take a while.  Returns true or false.
        Once it returns true, you can page through the stories with allProcessedInSubset
        '''
        subset_info = self.storySubsetDetail(subset_id)
        return (subset_info['ready']==1)

    def allProcessedInSubset(self,subset_id, page=1):
        '''
        Retrieve all the processed stories within a certain subset, 20 at a time
        '''
        return self._query( 'subset_processed/'+str(subset_id), { 'page':page }, 'GET' )


    def allProcessed(self, page=1):
        '''
        Return the last fully processed 20 stories (ie. with sentences pulled out)
        '''
        return self._query( 'all_processed', { 'page':page }, 'GET' )

    def storiesSince(self, story_id, count=DEFAULT_STORY_COUNT, fetch_raw_text=False):
        '''
        Return of list of stories with ids greater than the one specified
        '''
        return self._query('stories_query_json', 
            {'last_stories_id': story_id, 'story_count':count, 'raw_1st_download':(1 if fetch_raw_text else 0) } )
        
    def recentStories(self, story_count=DEFAULT_STORY_COUNT,  fetch_raw_text=False):
        '''
        Return of list of the most recent stories 
        '''
        return self._query('stories_query_json', 
            {'story_count':story_count, 'raw_1st_download':(1 if fetch_raw_text else 0)} )

    def storyDetail(self, story_id,  fetch_raw_text=False):
        '''
        Return the details about one story, by id
        '''
        return self._query('stories_query_json',
            {'start_stories_id':story_id, 'story_count':1, 'raw_1st_download':(1 if fetch_raw_text else 0) } )[0]
    
    def _query(self, method, params={}, http_method='PUT'):
        '''
        Helper that actually makes the requests
        '''
        url = self.API_URL + method
        if method=='stories_query_json':
            url = self.OLD_API_URL + method
        r = requests.request( http_method, url, 
            params=params,
            auth=(self._api_user, self._api_pass), 
            headers={ 'Accept': 'application/json'}  
        )
        return r.json()
