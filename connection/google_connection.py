from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config

client_config = {
    "web":{
        "client_id":Config.GOOGLE_CLIENT_ID,
        "project_id":"playlistbridge-api",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":Config.GOOGLE_CLIENT_SECRET,
        "redirect_uris":[Config.GOOGLE_REDIRECT_URI]
        }        
    }

GOOGLE_API_SCOPES = [
    'openid', 
    'https://www.googleapis.com/auth/userinfo.profile', 
    'https://www.googleapis.com/auth/userinfo.email'
]

class GoogleAuth:
    def __init__(self):
        self.flow = InstalledAppFlow.from_client_config(
            client_config, GOOGLE_API_SCOPES
        )
        self.flow.redirect_uri = Config.GOOGLE_REDIRECT_URI

    def get_auth_url(self):
        auth_url, _ = self.flow.authorization_url(prompt='consent')
        return auth_url

    def get_token(self, code):
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        print(credentials)
        return credentials.token

    def get_google_user_info(self):
        # Construir el servicio de Google People API para obtener la información del usuario
        credentials = self.flow.credentials  # Las credenciales ya obtenidas después de la autenticación
        service = build('oauth2', 'v2', credentials=credentials)
        
        # Hacer la solicitud para obtener la información del perfil del usuario
        user_info = service.userinfo().get().execute()

        print(user_info)
        
        return {
            "email": user_info['email'],
            "name": user_info.get('name'),
        }    





