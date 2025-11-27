import logging
import requests
import hashlib 
import time
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
import os # Ajouté, car souvent utile pour la configuration


# --- CONFIGURATION & ÉTATS ---

# Configuration du logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. URL BRUTE pour l'authentification initiale (valid_keys.txt)
# ⚠️ VÉRIFIEZ L'URL RAW DE VOTRE FICHIER valid_keys.txt SUR GITHUB
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/Elyseproduction/cl--d-acc-s-bot-telegram/main/valid_keys.txt"

# 2. ⚠️ À REMPLACER: TOKEN API DU BOT
BOT_TOKEN = "8277538492:AAFEpcyWDdQtldfobp0XaCXa0ELr_EpTyVg" 

# 3. ⚠️ À REMPLACER: VOTRE ID NUMÉRIQUE TÉLÉGRAM (Utilisé pour l'administration/logs)
ADMIN_ID = 7790337782 # REMPLACEZ PAR VOTRE ID NUMÉRIQUE

# 4. ⚠️ À REMPLACER: VOTRE NOM D'UTILISATEUR TÉLÉGRAM
ADMIN_USERNAME = "nambinintsoa36" # REMPLACEZ PAR VOTRE NOM D'UTILISATEUR

# 5. ⚠️ CORRECTION CRITIQUE: URL PUBLIQUE DE VOTRE SERVICE WEB DEPLOYÉ
# REMPLACEZ par l'adresse complète (ex: Render/Heroku) + /register_key
API_REGISTRATION_URL = "https://generator-ekhk.onrender.com/" 

# 6. ⚠️ À REMPLACER: Jeton secret de communication (DOIT ÊTRE IDENTIQUE au jeton du script API)
API_SECRET_TOKEN = "ElyseAppToken_12_06_2006_Madagascar"


# --- FONCTION D'APPEL À L'API D'ENREGISTREMENT ---

async def register_key_on_github(unique_id: str, username: str) -> bool:
    """Envoie l'ID unique à l'API du serveur pour l'ajout au fichier GitHub (license_codes.txt)."""
    payload = {
        "key": unique_id,
        "username": username,
        "file_to_update": "license_codes.txt", # Cible de l'écriture
        "secret_token": API_SECRET_TOKEN 
    }
    
    try:
        # L'appel POST est dirigé vers l'URL PUBLIQUE configurée ci-dessus
        response = requests.post(API_REGISTRATION_URL, json=payload, timeout=10)
        response.raise_for_status() 
        
        # Vérifie si le script API a renvoyé un statut de succès
        return response.status_code == 200 and response.json().get('status') == 'success'
    except requests.exceptions.RequestException as e:
        logger.error(f"Échec de l'enregistrement de la clé sur l'API: {e}")
        return False


async def handle_get_unique_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Génère un ID unique, l'envoie à l'API pour enregistrement sur license_codes.txt, puis l'affiche."""
    user = update.effective_user
    username = user.username if user.username else str(user.id)
    prefix = f"@{username}" if user.username else f"ID_{user.id}"
    
    # 1. Génération de l'ID unique (Logique de hachage)
    current_time_ms = int(time.time() * 1000)
    hash_object = hashlib.sha256(f"{prefix}-{current_time_ms}".encode())
    final_unique_id = hash_object.hexdigest()[:16] # Clé de 16 caractères

    # 2. Tentative d'enregistrement sur GitHub via l'API intermédiaire
    await update.message.reply_text("⏳ Tentative d'enregistrement de votre ID sur le serveur...")
    
    # 3. Appel à la fonction qui contacte l'API
    success = await register_key_on_github(final_unique_id, prefix)
    
    # 4. Affichage du résultat
    if success:
        message = (
            "✅ **ID UNIQUE GÉNÉRÉ AVEC SUCCÈS !**\n\n"
            f"Votre clé de licence est :\n`{final_unique_id}`\n\n"
            "Vous pouvez utiliser cette clé dans l'application client (`elyse_app.py`)."
        )
        await update.message.reply_markdown(message)
    else:
        error_message = (
            "❌ **ÉCHEC DE L'ENREGISTREMENT.**\n\n"
            "Une erreur est survenue lors de l'enregistrement de la clé sur le serveur.\n"
            "Veuillez vérifier les logs de l'API (`github_writer_api.py`) sur Render."
        )
        await update.message.reply_text(error_message)


# --- FONCTION DE DÉMARRAGE DU BOT ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Répond à la commande /start."""
    await update.message.reply_text("Bienvenue ! Utilisez /get_key pour générer une licence.")

def main() -> None:
    """Démarre le bot en mode polling."""
    try:
        # Construction de l'application avec le Jeton Bot
        application = Application.builder().token(BOT_TOKEN).build()

        # Ajout des gestionnaires de commandes
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("get_key", handle_get_unique_id))
        
        # Démarrage du bot (polling) - Ceci bloque l'exécution, d'où le besoin d'un worker 24/7
        logger.info("Bot démarré en mode Polling. Le Bot est en écoute...")
        application.run_polling(poll_interval=1.0)
    except Exception as e:
        # En cas d'erreur fatale (ex: Token API invalide)
        logger.error(f"Erreur fatale au démarrage ou lors de l'exécution: {e}")

if __name__ == '__main__':
    # Lance la fonction principale si le script est exécuté directement
    main()
