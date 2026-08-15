"""Interactive and Automated Terminal Demo for EMC Helpline Chatbot.

Provides a terminal interface for supervisors and evaluators:
- Interactive chat mode (FR, AR, Darija)
- Automated demo simulation mode with realistic typing effects
- Displays language detection, user profile, emergency alerts, sources, and RAG answers.

Usage:
    python demo_cli.py             # Interactive Mode
    python demo_cli.py --auto      # Automated Presentation Demo Mode
"""
import sys
import time
import argparse
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from services.chat_service import get_chat_service


# ============================================================
# ANSI Color Formatting
# ============================================================
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def type_print(text: str, delay: float = 0.005, color: str = ""):
    """Print text with a smooth typing animation effect."""
    for char in text:
        sys.stdout.write(f"{color}{char}{Colors.END}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_banner():
    """Display the EMC Helpline banner."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}" + "=" * 70)
    print("   🤖 EMC HELPLINE — CHATBOT IA MULTILINGUE D'ASSISTANCE")
    print("   Espace Maroc Cyberconfiance (EMC) — CMRPI")
    print("   Support : Français | Arabe Standard | Darija Marocain")
    print("=" * 70 + f"{Colors.END}\n")


def print_response(result: dict):
    """Format and print the chatbot response."""
    print(f"\n{Colors.GREEN}{Colors.BOLD}🤖 EMC Assistant :{Colors.END}")
    type_print(result["answer"], delay=0.004)

    # Metadata & Badges
    print(f"\n{Colors.CYAN}--- Métadonnées & Analyse ---{Colors.END}")
    lang_badge = f"{Colors.BOLD}{result['langue'].upper()}{Colors.END}"
    if result.get("is_darija"):
        lang_badge += f" {Colors.YELLOW}(Darija Détecté){Colors.END}"

    profile_badge = f"{Colors.BOLD}{result.get('user_profile', 'victim')}{Colors.END}"

    print(f"  • Langue        : {lang_badge}")
    print(f"  • Profil        : {profile_badge}")

    if result.get("is_urgent"):
        print(f"  • {Colors.RED}{Colors.BOLD}🚨 ALERTE URGENCE ACTIVÉE (Police 19 / Gendarmerie 177){Colors.END}")

    if result.get("sources"):
        print(f"  • Sources RAG utilisées :")
        for src in result["sources"][:3]:
            path = src.get("path") or "Base de connaissances"
            cat = src.get("categorie") or "general"
            print(f"    - [{cat}] {path}")

    print(f"{Colors.CYAN}" + "-" * 70 + f"{Colors.END}\n")


def run_interactive_mode():
    """Run interactive terminal chat loop."""
    print_banner()
    print(f"{Colors.YELLOW}Mode interactif démarré. Tapez votre message (ou 'quitter' pour sortir).{Colors.END}\n")

    chat_service = get_chat_service()
    session_id = None

    while True:
        try:
            user_input = input(f"{Colors.BOLD}👤 Vous : {Colors.END}").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quitter", "exit", "quit", "q"]:
                print(f"\n{Colors.GREEN}Merci d'avoir utilisé le Chatbot EMC. Au revoir !{Colors.END}\n")
                break

            print(f"{Colors.BLUE}⏳ Traitement RAG + Gemini en cours...{Colors.END}")
            result = chat_service.process_message(user_input, session_id=session_id)
            session_id = result["session_id"]
            print_response(result)

        except KeyboardInterrupt:
            print("\nInterruption. Au revoir !")
            break
        except Exception as e:
            print(f"{Colors.RED}Erreur : {e}{Colors.END}")


def run_automated_demo():
    """Run an automated presentation demo covering 4 key evaluation scenarios."""
    print_banner()
    print(f"{Colors.YELLOW}{Colors.BOLD}▶ LANCEMENT DE LA DÉMONSTRATION AUTOMATISÉE POUR SUPERVISEUR...{Colors.END}\n")
    time.sleep(1.5)

    scenarios = [
        {
            "title": "SCÉNARIO 1 : Victime de Sextorsion (Français)",
            "message": "Bonjour, je suis victime de chantage avec des photos intimes. Que dois-je faire ?",
            "pause": 3.0,
        },
        {
            "title": "SCÉNARIO 2 : Demande d'aide en Darija Marocain",
            "message": "واش نقدر نقدم شكاية على واحد كيهددني فالمواقع؟",
            "pause": 3.0,
        },
        {
            "title": "SCÉNARIO 3 : Détection de Situation d'Urgence et Danger Immédiat",
            "message": "Je suis en danger immédiat, la personne menace de venir chez moi maintenant !",
            "pause": 3.0,
        },
        {
            "title": "SCÉNARIO 4 : Parent inquiet pour son enfant",
            "message": "Mon enfant de 13 ans est harcelé sur les réseaux. Comment réagir en tant que parent ?",
            "pause": 2.0,
        },
    ]

    chat_service = get_chat_service()

    for idx, sc in enumerate(scenarios, 1):
        print(f"\n{Colors.HEADER}{Colors.BOLD}========================================================")
        print(f"  {sc['title']}")
        print(f"========================================================{Colors.END}\n")
        time.sleep(1.0)

        print(f"{Colors.BOLD}👤 Utilisateur : {Colors.END}", end="")
        type_print(sc["message"], delay=0.03, color=Colors.BOLD)
        time.sleep(0.8)

        print(f"{Colors.BLUE}⏳ Traitement RAG (ChromaDB) + Gemini 2.5 Flash...{Colors.END}")
        result = chat_service.process_message(sc["message"])
        time.sleep(0.5)

        print_response(result)
        time.sleep(sc["pause"])

    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS !{Colors.END}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EMC Helpline Chatbot Terminal Demo")
    parser.add_argument("--auto", action="store_true", help="Run automated demonstration mode")
    args = parser.parse_args()

    if args.auto:
        run_automated_demo()
    else:
        run_interactive_mode()
