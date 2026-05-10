import argparse
import hashlib
import time
import threading
import socket
import json
import os
from datetime import datetime
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN  = Fore.GREEN
    RED    = Fore.RED
    CYAN   = Fore.CYAN
    YELLOW = Fore.YELLOW
    MAGENTA = Fore.MAGENTA
    RESET  = Style.RESET_ALL
except ImportError:
    GREEN = RED = CYAN = YELLOW = MAGENTA = RESET = ""
SERVER_HOST    = "127.0.0.1"
SERVER_PORT    = 9999
MAX_ATTEMPTS   = 5          
LOCKOUT_TIME   = 30         
RATE_LIMIT     = 1.0        
DEFAULT_DELAY  = 0.1        
FAKE_USER_DB = {
    "admin":  hashlib.sha256("password123".encode()).hexdigest(),
    "root":   hashlib.sha256("toor".encode()).hexdigest(),
    "user":   hashlib.sha256("letmein".encode()).hexdigest(),
}
DEFAULT_WORDLIST = [
    "123456", "password", "password123", "admin", "letmein",
    "qwerty", "abc123", "monkey", "1234567", "dragon",
    "111111", "baseball", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "passw0rd", "shadow", "123123",
    "654321", "superman", "qazwsx", "michael", "football",
    "toor", "root", "pass", "test", "guest",
]
def print_banner():
    print(f"""
{CYAN}============================================
  🔓  Brute Force Simulator — Cyber Toolkit
============================================{RESET}""")
class LoginServer:
    def __init__(self):
        self.failed_attempts = {}   
        self.lockouts        = {}   
        self.last_attempt    = {}   
        self.lock            = threading.Lock()
    def is_locked_out(self, username):
        if username in self.lockouts:
            elapsed = time.time() - self.lockouts[username]
            if elapsed < LOCKOUT_TIME:
                remaining = int(LOCKOUT_TIME - elapsed)
                return True, remaining
            else:
                del self.lockouts[username]
                del self.failed_attempts[username]
        return False, 0
    def is_rate_limited(self, ip):
        if ip in self.last_attempt:
            elapsed = time.time() - self.last_attempt[ip]
            if elapsed < RATE_LIMIT:
                return True
        return False
    def attempt_login(self, username, password, ip):
        with self.lock:
            if self.is_rate_limited(ip):
                return {
                    "success": False,
                    "reason": "RATE_LIMITED",
                    "message": f"Too many requests. Slow down."
                }
            self.last_attempt[ip] = time.time()
            locked, remaining = self.is_locked_out(username)
            if locked:
                return {
                    "success": False,
                    "reason": "LOCKED_OUT",
                    "message": f"Account locked. Try again in {remaining}s."
                }
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if username in FAKE_USER_DB and FAKE_USER_DB[username] == hashed:
                self.failed_attempts.pop(username, None)
                return {
                    "success": True,
                    "reason": "SUCCESS",
                    "message": f"Login successful! Welcome, {username}."
                }
            else:
                self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
                attempts = self.failed_attempts[username]
                if attempts >= MAX_ATTEMPTS:
                    self.lockouts[username] = time.time()
                    return {
                        "success": False,
                        "reason": "LOCKED_OUT",
                        "message": f"Too many failed attempts. Account locked for {LOCKOUT_TIME}s."
                    }
                return {
                    "success": False,
                    "reason": "INVALID_CREDENTIALS",
                    "message": f"Invalid username or password. Attempt {attempts}/{MAX_ATTEMPTS}."
                }
    def handle_client(self, conn, addr):
        ip = addr[0]
        try:
            data = conn.recv(1024).decode()
            payload = json.loads(data)
            username = payload.get("username", "")
            password = payload.get("password", "")
            result = self.attempt_login(username, password, ip)
            status = f"{GREEN}SUCCESS{RESET}" if result["success"] else f"{RED}FAILED{RESET} ({result['reason']})"
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] {ip} → user={username!r:10} pass={password!r:15} {status}")
            conn.send(json.dumps(result).encode())
        except Exception as e:
            conn.send(json.dumps({"success": False, "reason": "ERROR", "message": str(e)}).encode())
        finally:
            conn.close()
    def start(self):
        print_banner()
        print(f"{CYAN} Mode    :{RESET} LOGIN SERVER")
        print(f"{YELLOW} Host    :{RESET} {SERVER_HOST}:{SERVER_PORT}")
        print(f"{YELLOW} Users   :{RESET} {', '.join(FAKE_USER_DB.keys())}")
        print(f"{YELLOW} Lockout :{RESET} After {MAX_ATTEMPTS} failed attempts ({LOCKOUT_TIME}s)")
        print(f"{YELLOW} Rate    :{RESET} Max 1 attempt per {RATE_LIMIT}s per IP")
        print(f"{CYAN}============================================{RESET}\n")
        print(f"{GREEN} Server running — waiting for connections...{RESET}\n")
        print(f" {'Time':<12} {'IP':<16} {'Result'}")
        print(f" {'-'*50}")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen(10)
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=self.handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
class BruteForcer:
    def __init__(self, target, port, username, wordlist, delay):
        self.target   = target
        self.port     = port
        self.username = username
        self.wordlist = wordlist
        self.delay    = delay
        self.attempts = 0
        self.found    = False
    def try_password(self, password):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))
            payload = json.dumps({"username": self.username, "password": password})
            sock.send(payload.encode())
            response = json.loads(sock.recv(1024).decode())
            sock.close()
            return response
        except Exception as e:
            return {"success": False, "reason": "CONNECTION_ERROR", "message": str(e)}
    def run(self):
        print_banner()
        print(f"{CYAN} Mode     :{RESET} ATTACKER")
        print(f"{YELLOW} Target   :{RESET} {self.target}:{self.port}")
        print(f"{YELLOW} Username :{RESET} {self.username}")
        print(f"{YELLOW} Wordlist :{RESET} {len(self.wordlist)} passwords")
        print(f"{YELLOW} Delay    :{RESET} {self.delay}s between attempts")
        print(f"{YELLOW} Started  :{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{CYAN}============================================{RESET}\n")
        start_time = time.time()
        for i, password in enumerate(self.wordlist, 1):
            if self.found:
                break
            self.attempts += 1
            result = self.try_password(password)
            if result["success"]:
                duration = time.time() - start_time
                self.found = True
                print(f"\n{GREEN}{'='*44}{RESET}")
                print(f"{GREEN}  ✅ PASSWORD FOUND!{RESET}")
                print(f"{GREEN}  Username : {self.username}{RESET}")
                print(f"{GREEN}  Password : {password}{RESET}")
                print(f"{GREEN}  Attempts : {self.attempts}{RESET}")
                print(f"{GREEN}  Duration : {duration:.2f}s{RESET}")
                print(f"{GREEN}{'='*44}{RESET}\n")
                return
            elif result["reason"] == "LOCKED_OUT":
                print(f"  [{i:>4}] {password:<20} {YELLOW}⚠ LOCKED OUT — waiting 35s...{RESET}")
                time.sleep(35)
                result = self.try_password(password)
                if result["success"]:
                    print(f"\n{GREEN}  ✅ PASSWORD FOUND after lockout: {password}{RESET}\n")
                    return
            elif result["reason"] == "RATE_LIMITED":
                print(f"  [{i:>4}] {password:<20} {YELLOW}⚠ RATE LIMITED — slowing down...{RESET}")
                time.sleep(2)
            else:
                print(f"  [{i:>4}] {password:<20} {RED}✗ Wrong{RESET}")
            time.sleep(self.delay)
        if not self.found:
            duration = time.time() - start_time
            print(f"\n{RED}============================================{RESET}")
            print(f"{RED}  ❌ Password not found in wordlist.{RESET}")
            print(f"{RED}  Attempts : {self.attempts}{RESET}")
            print(f"{RED}  Duration : {duration:.2f}s{RESET}")
            print(f"{RED}============================================{RESET}\n")
def load_wordlist(path):
    if path and os.path.exists(path):
        with open(path, "r", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]
        print(f"{GREEN} Loaded {len(words)} passwords from {path}{RESET}\n")
        return words
    else:
        print(f"{YELLOW} No wordlist file found — using built-in wordlist ({len(DEFAULT_WORDLIST)} passwords){RESET}\n")
        return DEFAULT_WORDLIST
def parse_args():
    parser = argparse.ArgumentParser(
        description="🔓 Cyber Toolkit — Brute Force Login Simulator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--mode", required=True, choices=["server", "attack"],
        help="Run mode:\n  server — Start the fake login server\n  attack — Run the brute force attacker"
    )
    parser.add_argument("--target",   default=SERVER_HOST, help=f"Target IP (default: {SERVER_HOST})")
    parser.add_argument("--port",     type=int, default=SERVER_PORT, help=f"Target port (default: {SERVER_PORT})")
    parser.add_argument("--username", default="admin", help="Username to attack (default: admin)")
    parser.add_argument("--wordlist", default=None, help="Path to wordlist file (default: built-in list)")
    parser.add_argument("--delay",    type=float, default=DEFAULT_DELAY, help=f"Delay between attempts in seconds (default: {DEFAULT_DELAY})")
    return parser.parse_args()
def main():
    args = parse_args()
    if args.mode == "server":
        server = LoginServer()
        server.start()
    elif args.mode == "attack":
        wordlist = load_wordlist(args.wordlist)
        attacker = BruteForcer(
            target   = args.target,
            port     = args.port,
            username = args.username,
            wordlist = wordlist,
            delay    = args.delay,
        )
        attacker.run()
if __name__ == "__main__":
    main()
