"""
label_gutenberg.py
------------------
Step 2b: Manual Labeling Tool

A simple terminal-based tool to label sentences from
Project Gutenberg novels with GoEmotions emotion labels.

This creates training/data/manual_labels.csv which is
automatically picked up by data_prep.py.

Usage (from backend/ folder):
    python training/label_gutenberg.py

Controls:
    Type the NUMBER of the emotion and press Enter
    Type 's' to skip a sentence
    Type 'q' to quit and save progress
    Type 'u' to undo the last label

Tips:
    - Aim for 30-50 examples per emotion
    - Focus on clear, unambiguous examples
    - Skip sentences that feel ambiguous
"""

import os
import csv
import sys

# ── Output file ───────────────────────────────────────────────────────────────
OUT_DIR   = os.path.join(os.path.dirname(__file__), "data")
OUT_FILE  = os.path.join(OUT_DIR, "manual_labels.csv")
os.makedirs(OUT_DIR, exist_ok=True)

# ── 28 GoEmotions labels ──────────────────────────────────────────────────────
LABELS = [
    "admiration", "amusement", "anger",       "annoyance",  "approval",
    "caring",     "confusion", "curiosity",   "desire",     "disappointment",
    "disapproval","disgust",   "embarrassment","excitement", "fear",
    "gratitude",  "grief",     "joy",          "love",       "nervousness",
    "neutral",    "optimism",  "pride",        "realization","relief",
    "remorse",    "sadness",   "surprise"
]

# ── Pre-loaded story sentences from Gutenberg (public domain) ─────────────────
# Add more sentences here as you like. These are from various novels.
SENTENCES = [
    # Pride and Prejudice
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
    "She was a woman of mean understanding, little information, and uncertain temper.",
    "\"I am sick of Mr. Bingley,\" cried his wife.",
    "He is also handsome, which a young man ought likewise to be, if he possibly can.",
    "She began now to comprehend that he was exactly the man who, in disposition and talents, would most suit her.",
    "Her heart was divided between concern for her sister and resentment against all the others.",
    "Elizabeth felt herself completely taken in.",
    "She could not think of Darcy's leaving Kent without remembering that his cousin was to go with him.",
    "With a triumphant smile they were told, that it was ten miles round.",
    "She was not rendered formidable by silence.",

    # Great Expectations
    "I never had one hour's happiness in her society, and yet my mind all round the four-and-twenty hours was harping on the happiness of having her with me unto death.",
    "Take nothing on its looks; take everything on evidence. There's no better rule.",
    "I knew I was common, and that I wished I was not common.",
    "He called the knaves, Jacks, this boy! said Estella with disdain.",
    "I looked at the stars, and considered how awful it would be for a man to turn his face up to them as he froze to death.",
    "Pip, dear old chap, life is made of ever so many partings welded together.",
    "Pause you who read this, and think for a moment of the long chain of iron or gold, of thorns or flowers.",
    "We spent as much money as we could, and got as little for it as people could make up their minds to give us.",
    "Herbert and I went on from bad to worse, in the way of increasing our debts, looking into our affairs, leaving our affairs open.",
    "There was a long hard time when I kept far from me the remembrance of what I had thrown away.",

    # The Picture of Dorian Gray
    "To define is to limit.",
    "The books that the world calls immoral are books that show the world its own shame.",
    "The only way to get rid of a temptation is to yield to it.",
    "He was always late on principle, his principle being that punctuality is the thief of time.",
    "I don't want to be at the mercy of my emotions. I want to use them, to enjoy them, and to dominate them.",
    "Behind every exquisite thing that existed, there was something tragic.",
    "Nowadays people know the price of everything and the value of nothing.",
    "Children begin by loving their parents; as they grow older they judge them; sometimes they forgive them.",
    "Experience is merely the name men gave to their mistakes.",
    "The books that the world calls immoral are books that show the world its own shame.",

    # Jane Eyre
    "I am no bird; and no net ensnares me: I am a free human being with an independent will.",
    "I would always rather be happy than dignified.",
    "Feeling without judgment is a washy draught indeed; but judgment untempered by feeling is too bitter and husky a morsel for human deglutition.",
    "I had not intended to love him; the reader knows I had wrought hard to extirpate from my soul the germs of love there detected.",
    "Do you think I am an automaton? — a machine without feelings?",
    "The most tranquil, even the most resigned, are not necessarily the most happy.",
    "I would not exchange this one little English girl for the Grand Turk's whole seraglio.",
    "All my heart is yours, sir: it belongs to you; and with you it would remain, were fate to exile the rest of me from your presence forever.",
    "I sometimes have a queer feeling with regard to you — especially when you are near me, as now: it is as if I had a string somewhere under my left ribs.",
    "There is no happiness like that of being loved by your fellow-creatures.",

    # A Tale of Two Cities
    "It was the best of times, it was the worst of times.",
    "A wonderful fact to reflect upon, that every human creature is constituted to be that profound secret and mystery to every other.",
    "I see a beautiful city and a brilliant people rising from this abyss.",
    "It is a far, far better thing that I do, than I have ever done; it is a far, far better rest that I go to than I have ever known.",
    "You have been the last dream of my soul.",
    "recalled to life",
    "\"You know that I am incapable of all the higher and better flights of men,\" he said. \"If you doubt it, ask Stryver.\"",
    "The night was dark and cold, and the wind was blowing hard.",

    # Wuthering Heights
    "He's more myself than I am. Whatever our souls are made of, his and mine are the same.",
    "If he loved with all the powers of his puny being, he couldn't love as much in eighty years as I could in a day.",
    "I have not broken your heart — you have broken it; and in breaking it, you have broken mine.",
    "Terror made me cruel.",
    "I cannot live without my life! I cannot live without my soul!",
    "Nelly, I am Heathcliff! He's always, always in my mind: not as a pleasure, any more than I am always a pleasure to myself, but as my own being.",
    "Oh, cried Catherine, in a tone of vexation, I'm tired — I'm stalled, Hareton!",

    # The Jungle
    "They were beaten; they had lost the game, they were swept aside.",
    "He had no wit to see that here was a new religion for him — that here was his chance.",
    "It was all so very business-like that one watched it fascinated.",

    # Custom narrative sentences (generic story-type)
    "She ran toward the burning building without a second thought, tears streaming down her face.",
    "The silence in the room was deafening after the news had broken.",
    "He laughed so hard his sides ached, tears of joy blurring his vision.",
    "She had waited for this moment her entire life, and now that it had arrived, she could barely breathe.",
    "He looked down at the letter, reading it three times before the words began to make sense.",
    "The realization hit him like a wave — she was never coming back.",
    "She felt a warmth bloom in her chest as he finally said the words she had longed to hear.",
    "His hands shook as he stepped onto the stage, five hundred faces staring up at him.",
    "She closed her eyes, exhaling slowly, letting the last of the tension melt from her shoulders.",
    "The betrayal stung more than any physical wound he had ever known.",
]


def load_existing_labels():
    if not os.path.exists(OUT_FILE):
        return [], set()
    rows = []
    texts = set()
    with open(OUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            texts.add(row["text"])
    return rows, texts


def save_labels(rows):
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)


def print_menu():
    print("\n" + "─" * 50)
    print("EMOTION LABELS:")
    for i, label in enumerate(LABELS):
        print(f"  {i:>2}. {label}")
    print("─" * 50)
    print("   s = skip   |   u = undo   |   q = quit & save")
    print("─" * 50)


def main():
    print("=" * 60)
    print("KahaaniVani.ai — Story Sentence Labeling Tool")
    print("=" * 60)
    print(f"Output: {OUT_FILE}")

    labeled_rows, already_labeled_texts = load_existing_labels()
    print(f"Already labeled: {len(labeled_rows)} sentences")

    # Filter to unlabeled sentences
    todo = [s for s in SENTENCES if s not in already_labeled_texts]
    print(f"Remaining in this batch: {len(todo)} sentences")

    if not todo:
        print("\nAll pre-loaded sentences are labeled!")
        print("Add more sentences to the SENTENCES list in this file.")
        return

    print_menu()

    for sentence in todo:
        print(f"\n\033[1mSentence:\033[0m")
        print(f"  \"{sentence}\"")

        while True:
            choice = input("\nYour label (number / s / u / q): ").strip().lower()

            if choice == "q":
                save_labels(labeled_rows)
                print(f"\nSaved {len(labeled_rows)} labels to {OUT_FILE}")
                print("Run data_prep.py to include these in your training set.")
                sys.exit(0)

            elif choice == "s":
                print("  → Skipped.")
                break

            elif choice == "u":
                if labeled_rows:
                    removed = labeled_rows.pop()
                    already_labeled_texts.discard(removed["text"])
                    print(f"  → Undid: \"{removed['text'][:50]}...\" → {removed['label']}")
                    # re-add to front of todo
                    todo.insert(0, removed["text"])
                else:
                    print("  → Nothing to undo.")
                break

            elif choice.isdigit() and 0 <= int(choice) < len(LABELS):
                label = LABELS[int(choice)]
                labeled_rows.append({"text": sentence, "label": label})
                already_labeled_texts.add(sentence)
                print(f"  → Labeled as: \033[32m{label}\033[0m")
                break

            else:
                print(f"  Invalid input. Enter a number 0-{len(LABELS)-1}, 's', 'u', or 'q'.")

    # Finished all sentences
    save_labels(labeled_rows)
    print(f"\n✓ All sentences labeled! Total: {len(labeled_rows)}")
    print(f"  Saved to: {OUT_FILE}")
    print("\nNext step: python training/data_prep.py")


if __name__ == "__main__":
    main()
