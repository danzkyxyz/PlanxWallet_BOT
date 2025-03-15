import requests
import time
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("claim_task.log"),
            logging.StreamHandler()
        ]
    )

def get_tokens():
    try:
        with open("token.txt", "r") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
            if not tokens:
                logging.error("token.txt is empty! Please update your token.")
                return []
            tokens = ["Bearer " + token if not token.startswith("Bearer ") else token for token in tokens]
            logging.info(f"Loaded {len(tokens)} tokens.")
            return tokens
    except FileNotFoundError:
        logging.error("token.txt not found. Please add your token manually.")
        return []

def validate_token(token):
    url = "https://mpc-api.planx.io/api/v1/telegram/info"
    headers = {"Authorization": token, "token": token}
    response = requests.get(url, headers=headers)
    
    logging.info(f"Validating token: {token[:30]}... (truncated)")
    if response.status_code == 200 and response.json().get("success"):
        logging.info("Token is valid!")
        return True
    else:
        logging.error(f"Token validation failed: {response.text}")
        return False

def call_task(token, task_id):
    url = "https://mpc-api.planx.io/api/v1/telegram/task/call"
    headers = {
        "Authorization": token,
        "token": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://tg-wallet.planx.io",
        "Referer": "https://tg-wallet.planx.io/"
    }
    payload = {"taskId": task_id}
    
    logging.info(f"Calling task: {task_id}")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200 and response.json().get("success"):
        logging.info(f"Task {task_id} successfully called!")
        return True
    else:
        logging.error(f"Failed to call task {task_id}: {response.text}")
        return False

def claim_task(token, task_id):
    url = "https://mpc-api.planx.io/api/v1/telegram/task/claim"
    headers = {
        "Authorization": token,
        "token": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://tg-wallet.planx.io",
        "Referer": "https://tg-wallet.planx.io/"
    }
    payload = {"taskId": task_id}
    
    logging.info(f"Attempting to claim task: {task_id}")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == "200":
            logging.info(f"Task {task_id} claimed successfully!")
            return True
        elif "already claimed" in result.get("message", "").lower():
            logging.info(f"Task {task_id} already claimed!")
            return False
    logging.error(f"Failed to claim task {task_id}: {response.text}")
    return False

def main_loop():
    setup_logging()
    tokens = get_tokens()
    
    if not tokens:
        logging.error("No tokens found. Please update token.txt and restart.")
        return
    
    task_ids = [
        "m20250212173934013124700001",
        "m20250212173935571986800022", "m20250212173935594680500028", "m20250212173935584402900025", 
        "m20250212173935604389100031", "m20250212173935613755700034", "m20250214173952165258600005", 
        "m20250213173941632390600015", "m20250213173941720460300018", "m20250214173952169399300006", 
        "m20250213173941728955700021", "m20250213173941736560000024", "m20250213173941767785900027", 
        "m20250212173935456044700010", "m20250212173935470203200013", "m20250212173935480395100016", 
        "m20250212173935519374200019"
    ]
    
    for token in tokens:
        if not validate_token(token):
            logging.error("Skipping invalid token.")
            continue
        
        for task_id in task_ids:
            call_task(token, task_id)
            time.sleep(5)  
        
        logging.info("Waiting 10 second before claiming tasks...")
        time.sleep(10)  
        
        for task_id in task_ids:
            claim_task(token, task_id)
            time.sleep(5)  
        
    logging.info("Waiting 3 hours before next round...")
    time.sleep(10800)  

if __name__ == "__main__":
    main_loop()
