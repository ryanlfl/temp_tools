from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file_path = ('.env',)

class Config(BaseSettings):
    
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding='utf-8')

    here_maps_user_id : SecretStr
    here_maps_client_id : SecretStr
    here_maps_token_endpoint_url : str
    here_maps_access_key_id : SecretStr
    here_maps_access_key_secret : SecretStr
    

config = Config()

if __name__ == "__main__":
    print(config.here_maps_access_key_id.get_secret_value())