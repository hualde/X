import argparse
import os
import sys
from pathlib import Path
from typing import Tuple

import tweepy
from dotenv import load_dotenv


def load_credentials() -> dict:
    """
    Carga y valida las credenciales de la API de X desde el archivo .env.
    Returns:
        dict: Diccionario que contiene las claves de autenticación requeridas.  
    Raises:
        ValueError: Si alguna de las credenciales no está configurada.
    """
    load_dotenv()
    credentials = {
        "api_key": os.getenv("X_API_KEY"),
        "api_secret": os.getenv("X_API_SECRET"),
        "access_token": os.getenv("X_ACCESS_TOKEN"),
        "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET"),
    }
    
    for key, value in credentials.items():
        if not value:
            raise ValueError(f"Falta la credencial {key}. Por favor configúrala en el archivo .env.")
            
    return credentials


def get_twitter_clients(credentials: dict) -> Tuple[tweepy.Client, tweepy.API]:
    """
    Autentica y devuelve los clientes de Tweepy (v2 y v1.1).
    Args:
        credentials (dict): Credenciales cargadas con `load_credentials`.
    Returns:
        Tuple[tweepy.Client, tweepy.API]: 
            El cliente v2 se usa para publicar el tweet.
            El cliente v1.1 se usa para subir archivos multimedia, ya que
            la carga de media requiere v1.1 en el tier gratuito actual.
    """
    # Cliente para API v2 (creación de tweets)
    client = tweepy.Client(
        consumer_key=credentials["api_key"],
        consumer_secret=credentials["api_secret"],
        access_token=credentials["access_token"],
        access_token_secret=credentials["access_token_secret"]
    )
    
    # Cliente para API v1.1 (subida de imágenes)
    auth = tweepy.OAuth1UserHandler(
        credentials["api_key"],
        credentials["api_secret"],
        credentials["access_token"],
        credentials["access_token_secret"]
    )
    api = tweepy.API(auth)
    return client, api

def validate_image(image_path_str: str) -> Path:
    """
    Verifica que la imagen especificada exista y no exceda el límite permitido por la API (5MB).
    Args:
        image_path_str (str): Ruta al archivo de imagen provista por la CLI. 
    Returns:
        Path: Objeto pathlib.Path apuntando a una ruta válida y dentro del tamaño permitido.
    Raises:
        FileNotFoundError: Si la ruta de la imagen no existe.
        ValueError: Si no es un archivo o si excede los 5MB.
    """
    path = Path(image_path_str)
    
    if not path.exists():
        raise FileNotFoundError(f"No se encontró la imagen en la ruta: {image_path_str}")
        
    if not path.is_file():
        raise ValueError(f"La ruta proporcionada no es un archivo: {image_path_str}")
        
    # Validar que el archivo no sea mayor a 5MB (Límite de la API para fotos)
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > 5.0:
        raise ValueError(
            f"La imagen es demasiado grande. "
            f"El tamaño es de {file_size_mb:.2f}MB, y el límite máximo permitido por X es de 5MB."
        )
        
    return path


def post_tweet(text: str, image_path: str = None) -> None:
    """
    Maneja el flujo de publicación del tweet y subida de media si se especifica.
    Args:
        text (str): Contenido de texto del tweet.
        image_path (str, optional): Ruta a la imagen si se desea adjuntar una. 
    """
    try:
        credentials = load_credentials()
        client, api = get_twitter_clients(credentials)
        
        media_id = None
        if image_path:
            valid_path = validate_image(image_path)
            print(f"Subiendo imagen '{valid_path}' a los servidores de X...")
            
            # Para el upload en v1.1
            media = api.media_upload(filename=str(valid_path))
            media_id = media.media_id_string
            print(f"✅ Imagen subida correctamente. Media ID = {media_id}")
            
        print(f"Publicando tweet: '{text}'...")
        if media_id:
            # Tweet con adjunto usando v2
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            # Tweet de solo texto usando v2
            response = client.create_tweet(text=text)
            
        tweet_id = response.data['id']
        print(f"✅ ¡Éxito! El tweet ha sido publicado correctamente.")
        print(f"🆔 ID del tweet: {tweet_id}")
        print(f"🔗 URL: https://twitter.com/user/status/{tweet_id}")
        
    except ValueError as val_err:
        print(f"❌ Error de validación: {val_err}", file=sys.stderr)
    except FileNotFoundError as fnf_err:
        print(f"❌ Error de archivo: {fnf_err}", file=sys.stderr)
    except tweepy.errors.Unauthorized:
        print("❌ Error de autenticación: Las credenciales son inválidas. Revisa tu archivo .env.", file=sys.stderr)
        print("   Asegúrate también de tener el 'User context authentication' configurado.", file=sys.stderr)
    except tweepy.errors.TooManyRequests:
        print("❌ Error Rate Limit: Has excedido el límite de peticiones permitido por la API.", file=sys.stderr)
    except tweepy.errors.Forbidden as for_err:
        print(f"❌ Error de Permisos (Forbidden): {for_err}", file=sys.stderr)
        print("   ¿El nivel de tu app en Developer Portal es 'Read and write'?", file=sys.stderr)
    except tweepy.errors.TweepyException as tweepy_err:
        print(f"❌ Error general en la API de X o error de red: {tweepy_err}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error inesperado: {e}", file=sys.stderr)
        

def main():
    """
    Función de entrada para parsear argumentos y ejecutar el flujo de publicación.
    """
    parser = argparse.ArgumentParser(
        description="Script para publicar en X (Twitter) un tweet con texto y (opcionalmente) una imagen."
    )
    
    parser.add_argument(
        "--text", 
        required=True, 
        type=str, 
        help="El texto del tweet que quieres publicar (obligatorio)."
    )
    parser.add_argument(
        "--image", 
        required=False, 
        type=str, 
        help="Ruta hacia la imagen que quieres subir junto al tweet (opcional)."
    )
    
    args = parser.parse_args()
    post_tweet(text=args.text, image_path=args.image)


if __name__ == "__main__":
    main()
