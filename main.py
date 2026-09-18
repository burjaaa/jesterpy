import asyncio
import pyperclip
import aiohttp
from models import JokeFetcher, Joke
from storage import HistoryStorage

CATEGORIES = ["Any", "Programming", "Misc", "Dark", "Pun", "Spooky", "Christmas"]

class JokeApp:
    def __init__(self):
        self.fetcher = JokeFetcher()
        self.storage = HistoryStorage()

    async def get_and_display_joke(self, category: str = "Any"):
        print(f"\n[...] Fetching {category} joke...")
        
        async with aiohttp.ClientSession() as session:
            try:
                joke = await self.fetcher.fetch_joke(session, category)
                print("\n" + "=" * 45)
                print(f"Category: {joke.category} | Type: {joke.content_type}")
                print("-" * 45)
                print(f"{joke.full_text}")
                print("=" * 45)

                copy_choice = input("\nCopy joke to clipboard? (y/n): ").strip().lower()
                if copy_choice == 'y':
                    try:
                        pyperclip.copy(joke.full_text)
                        print("[✓] Copied to clipboard!")
                    except Exception as e:
                        print(f"[x] Failed to copy: {e}")


                choice = input("\nSave this joke to your history? (y/n): ").strip().lower()
                if choice == 'y':
                    saved = self.storage.save_joke(joke)
                    if saved:
                        print("[✓] Joke saved successfully!")
                    else:
                        print("[!] Joke is already in your saved collection.")
            except Exception as e:
                print(f"[x] Error fetching joke: {e}")
                
    def view_saved_jokes(self):
        jokes = self.storage.load_jokes()
        if not jokes:
            print("\n[!] No saved jokes in history.")
            return

        print("\n" + "=" * 45)
        print("               SAVED JOKES                 ")
        print("=" * 45)
        for idx, joke in enumerate(jokes, 1):
            print(f"[{idx}] ({joke.category}) - ID: {joke.item_id}")
            print(f"    {joke.full_text}")
            print("-" * 45)

    def delete_joke_menu(self):
        jokes = self.storage.load_jokes()
        if not jokes:
            print("\n[!] No saved jokes to delete.")
            return

        self.view_saved_jokes()
        try:
            choice = int(input("\nEnter the number of the joke to delete: "))
            if self.storage.delete_joke(choice - 1):
                print("[✓] Joke deleted successfully.")
            else:
                print("[!] Invalid index.")
        except ValueError:
            print("[!] Please enter a valid number.")

    def filter_jokes_menu(self):
        cat = input("Enter category to filter (e.g. Programming, Misc, Pun): ").strip()
        filtered = self.storage.filter_by_category(cat)
        if not filtered:
            print(f"\n[!] No saved jokes found in category '{cat}'.")
            return

        print(f"\n--- Saved Jokes in '{cat}' ---")
        for idx, joke in enumerate(filtered, 1):
            print(f"[{idx}] {joke.full_text}")

    async def run(self):
        while True:
            print("\n=== JOKE / QUOTE DAILY COLLECTOR ===")
            print("1. Get Random Joke")
            print("2. Get Joke by Category")
            print("3. View Saved Jokes")
            print("4. Filter Saved Jokes by Category")
            print("5. Delete Saved Joke")
            print("6. Exit")

            choice = input("Select an option (1-6): ").strip()
            if choice == "1":
                await self.get_and_display_joke("Any")
            elif choice == "2":
                print("\nCategories: " + ", ".join(CATEGORIES[1:]))
                cat = input("Type category: ").strip()
                await self.get_and_display_joke(cat if cat else "Any")
            elif choice == "3":
                self.view_saved_jokes()
            elif choice == "4":
                self.filter_jokes_menu()
            elif choice == "5":
                self.delete_joke_menu()
            elif choice == "6":
                print("\nGoodbye!")
                break
            else:
                print("[!] Invalid option. Try again.")

if __name__ == "__main__":
    app = JokeApp()
    asyncio.run(app.run())