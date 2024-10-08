from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config

client_config = {
    "web":{
        "client_id":Config.YOUTUBE_CLIENT_ID,
        "project_id":"playlistbridge-api",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":Config.YOUTUBE_CLIENT_SECRET,
        "redirect_uris":[Config.YOUTUBE_REDIRECT_URI]
        }        
    }

YOUTUBE_API_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubeAuth:
    def __init__(self):
        self.flow = InstalledAppFlow.from_client_config(
            client_config, YOUTUBE_API_SCOPES
        )
        self.flow.redirect_uri = Config.YOUTUBE_REDIRECT_URI

    def get_auth_url(self):
        auth_url, _ = self.flow.authorization_url(prompt='consent')
        return auth_url

    def get_token(self, code):
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials


        service = build('people', 'v1', credentials=credentials)
        
        # Llama a la API para obtener el perfil del usuario
        user_profile = service.people().get(resourceName='people/me', personFields='names,emailAddresses,photos').execute()
        
        # Extrae la información que necesitas del perfil
        user_info = {
            'name': user_profile.get('names', [{}])[0].get('displayName', None),
            'email': user_profile.get('emailAddresses', [{}])[0].get('value', None),            
        }
        print(user_info)
        
        return credentials.token





