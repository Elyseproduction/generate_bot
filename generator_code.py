import logging
import requests
import hashlib 
# ... (autres imports) ...

# --- CONFIGURATION & ÉTATS ---

# ... (Définitions d'états) ...

# 1. URL BRUTE pour l'authentification initiale (valid_keys.txt)
# ⚠️ VÉRIFIEZ L'URL DE VOTRE FICHIER valid_keys.txt
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/Elyseproduction/cl--d-acc-s-bot-telegram/main/valid_keys.txt"

# 2. ⚠️ À REMPLACER: TOKEN API DU BOT
BOT_TOKEN = "8277538492:AAFEpcyWDdQtldfobp0XaCXa0ELr_EpTyVg" 

# 3. ⚠️ À REMPLACER: VOTRE ID NUMÉRIQUE TÉLÉGRAM
ADMIN_ID = 7790337782 

# 4. ⚠️ À REMPLACER: VOTRE NOM D'UTILISATEUR TÉLÉGRAM
ADMIN_USERNAME = "nambinintsoa36"

# 5. ⚠️ À REMPLACER: URL DE VOTRE SERVICE WEB (L'adresse IP/domaine où vous avez hébergé le script API)
API_REGISTRATION_URL = "https://generator-ekhk.onrender.com"

# 6. ⚠️ À REMPLACER: Jeton secret de communication (DOIT ÊTRE IDENTIQUE au jeton du script API)
API_SECRET_TOKEN = "UN_JETON_SECRET_FORT_QUE_VOUS_DEFINISSEZ"


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
        response = requests.post(API_REGISTRATION_URL, json=payload, timeout=10)
        response.raise_for_status() 
        return response.status_code == 200 and response.json().get('status') == 'success'
    except requests.exceptions.RequestException as e:
        logger.error(f"Échec de l'enregistrement de la clé sur l'API: {e}")
        return False


async def handle_get_unique_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Génère un ID unique, l'envoie à l'API pour enregistrement sur license_codes.txt, puis l'affiche."""
    user = update.effective_user
    # 1. Génération de l'ID unique (Logique inchangée)
    # ... (code de génération de final_unique_id) ...
    
    # 2. Tentative d'enregistrement sur GitHub via l'API intermédiaire
    await update.message.reply_text("⏳ Tentative d'enregistrement de votre ID sur le serveur...")
    
    success = await register_key_on_github(final_unique_id, prefix)
    
    # ... (Affichage des messages de succès/échec) ...
