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

    # ── GRIEF (target: 40 examples) ──────────────────────────────────────────
    # Label all of these as: 16 (grief)
    "She wept until there were no more tears left, and then she simply sat in the silence of her loss.",
    "He placed the flowers on the grave and stood there for a long time, not speaking, not moving.",
    "The house felt unbearably empty without her — every room a reminder of what was gone.",
    "She kept his coat hanging by the door long after he had passed, unable to bring herself to move it.",
    "Grief, she discovered, was not loud. It was the quietest, most suffocating thing she had ever known.",
    "He had lost many things in his life, but nothing had prepared him for the weight of this absence.",
    "The child asked where grandmother had gone, and nobody could answer.",
    "She held the photograph for hours, tracing the lines of a face she would never see again.",
    "The funeral was over, the guests had left, and now there was only the unbearable ordinary of a world without him.",
    "He could not bring himself to delete her number from his phone.",
    "She heard his favourite song on the radio and had to pull over to the side of the road.",
    "The loss settled into her bones like winter — permanent, aching, cold.",
    "He stood at the edge of the grave and felt the world tilt beneath him.",
    "Every morning she woke and remembered, and the remembering was its own kind of death.",
    "She buried her face in his pillow and breathed in what little was left of him.",
    "The grief was not something she could explain to anyone who had not lived it.",
    "He carried the weight of his brother's absence like a stone in his chest.",
    "She returned to the places they had loved together and found them unbearable.",
    "There is a particular cruelty in losing someone slowly, watching them fade before your eyes.",
    "He did not cry at the funeral. He cried three weeks later, alone in his car in a car park.",
    "She tried to grieve quietly so as not to burden others, but quiet grief is its own torment.",
    "The anniversary arrived, as it always did, like a wound reopened.",
    "She sorted through his belongings in silence, holding each object like a relic.",
    "Time does not heal all wounds. It simply teaches you to carry them differently.",
    "He missed her in the small, stupid moments — choosing a restaurant, watching a film alone.",
    "The word 'gone' did not feel real. None of it felt real.",
    "She sat at the kitchen table and could not eat, could not speak, could not be.",
    "He lay awake at night replaying their last conversation, wishing he had said more.",
    "The grief came in waves, and some days the waves were so large she could not stand.",
    "She learned that mourning has no schedule, no logic, no end.",

    # ── NERVOUSNESS (target: 40 examples) ────────────────────────────────────
    # Label all of these as: 19 (nervousness)
    "His palms were damp, his heart hammering as he waited for his name to be called.",
    "She could not sit still — she paced the length of the room again and again.",
    "He rehearsed the words in his head a hundred times, but when the moment came, they vanished.",
    "Her stomach was a tight fist of anxiety as she stood outside the interview room.",
    "He kept checking his phone, then the clock, then the door, unable to settle.",
    "She felt the familiar nausea rising in her throat and pressed her hands together to stop them shaking.",
    "Every footstep on the stairs made her flinch.",
    "He could not eat the night before. He lay awake, running every possible outcome through his mind.",
    "She tugged at the hem of her jacket, suddenly acutely aware of how she looked.",
    "The waiting was worse than anything that came after.",
    "He swallowed hard and stepped forward, willing his legs to stop trembling.",
    "She kept her voice steady through an act of sheer will, though everything inside her was screaming.",
    "What if something went wrong? The thought circled his mind without stopping.",
    "She stood at the edge of the crowd, too anxious to go in, too stubborn to leave.",
    "His breathing had become shallow, each exhale a small, controlled act.",
    "She bit the inside of her cheek to stop herself from speaking before she was ready.",
    "He arrived thirty minutes early, which made the waiting worse.",
    "She read the message six times and still could not decide how to reply.",
    "The thought of standing up in front of all those people made him feel physically ill.",
    "Her hands refused to do what she told them.",
    "He laughed too loudly at the wrong moment, a nervous reflex he could not control.",
    "She typed the email and then stared at the send button for three full minutes.",
    "He felt certain, in the way that only anxiety can make you certain, that everything was about to go wrong.",
    "She pressed her back against the wall and took a slow breath, trying to remember that she was fine.",
    "The stage looked enormous from the wings.",
    "He could feel every eye in the room on him, even the ones that were not.",
    "She had done this a hundred times before, but tonight, it felt new and terrifying.",
    "He read the questions on the exam paper and felt his mind go perfectly, horribly blank.",
    "She smiled and nodded and said she was fine, all while her heart tried to escape through her ribs.",
    "He triple-checked the locks before bed. Then checked them again.",

    # ── OPTIMISM (target: 40 examples) ──────────────────────────────────────
    # Label all of these as: 21 (optimism)
    "She believed, despite everything, that things would turn out well in the end.",
    "It was not naivety. It was a deliberate choice to expect good things.",
    "He told himself: tomorrow will be better. And he meant it.",
    "She planted seeds in the garden and felt, doing so, a profound sense of possibility.",
    "There was still time. That was the thought that kept her going — there was still time.",
    "He could see, for the first time in a long while, how things might improve.",
    "She did not know what was coming, but she felt certain it would be good.",
    "Every difficulty was temporary. She held to this like a rope.",
    "He made his plans with enthusiasm, undeterred by what had happened before.",
    "She woke with the conviction that today would be different.",
    "The future shimmered ahead of him, full of things not yet decided.",
    "She wrote down her goals and felt a surge of genuine belief that she would achieve them.",
    "They had very little, but they had each other, and they were certain that was enough to build on.",
    "He walked out of the building and into the sunlight and thought: this is not the end.",
    "She had been knocked down before. She knew how to get up.",
    "There is always another door, she told him. Always another way through.",
    "He could not afford to despair. So he chose hope, deliberately, every morning.",
    "She let herself imagine the best possible outcome, and found she almost believed in it.",
    "The city stretched before them, full of strangers and chances.",
    "Whatever happened next, they would face it. They would figure it out.",
    "He had learned that optimism was not the absence of fear — it was moving forward despite it.",
    "She told her children: hard times do not last. Good people do.",
    "He saw the wreckage of what had been and began immediately to think about what might be built next.",
    "She was not certain, but she was hopeful, and hopeful felt like enough.",
    "Tomorrow was unwritten. He found this thought, for the first time, exhilarating rather than frightening.",
    "She closed the chapter on the worst year of her life and opened a clean page.",
    "He chose to believe that the people around him were trying their best. It made the world easier to inhabit.",
    "Things had been dark. But she had seen the dark end before.",
    "He could see, past the difficulty, a version of his life that was genuinely good.",
    "She was learning that hope was not a feeling. It was a practice.",

    # ── REALIZATION (target: 40 examples) ───────────────────────────────────
    # Label all of these as: 23 (realization)
    "It struck her all at once — she had been wrong. Completely, terribly wrong.",
    "He stared at the evidence in front of him and felt the world rearrange itself.",
    "The truth arrived slowly at first, then all at once, like a flood.",
    "She understood now what she had not understood before, and the understanding changed everything.",
    "For a long moment he simply stood there, letting the knowledge settle.",
    "It occurred to her, with sudden clarity, that nothing would ever be the same.",
    "He saw what he had refused to see, and the seeing of it was a kind of violence.",
    "She realised, too late, what she had done.",
    "The penny dropped, as they say, and when it did, she felt everything shift.",
    "He had been operating on the wrong assumption for months. Now he knew.",
    "There was a moment — she could pinpoint it exactly — when she understood.",
    "It was not what he had been told. It was something else entirely. He saw this now.",
    "She had thought she understood the situation. She had been catastrophically mistaken.",
    "The realization came not as a comfort but as a rupture.",
    "He turned the fact over in his mind, examining it from every angle, and felt his certainties dissolve.",
    "It dawned on her, in the quiet of the night, what the strange remark had meant.",
    "He had been looking at the problem from the wrong side all along.",
    "The solution was obvious — once you saw it, you could not understand why you had not seen it before.",
    "She had spent years being angry at the wrong person.",
    "He realized, somewhere in the middle of the argument, that he was not angry at her. He was afraid.",
    "The patterns, once she saw them, were everywhere.",
    "It came to her in the shower — the piece she had been missing for weeks.",
    "He looked at his life from the outside, as if for the first time, and was startled by what he saw.",
    "She understood, reading the letter, that the story she had told herself was false.",
    "The answer arrived without warning, at three in the morning, in the space between sleeping and waking.",
    "He saw his own reflection in what she was describing, and the recognition was uncomfortable.",
    "All the small details that had seemed unconnected suddenly formed a picture.",
    "She had not wanted to see it. But now that she had, there was no going back.",
    "He stopped mid-sentence as the implication of his own words became clear to him.",
    "It was not until much later that she understood what that day had actually cost her.",

    # ── PRIDE (target: 35 examples) ──────────────────────────────────────────
    # Label all of these as: 22 (pride)
    "She stood on the podium and felt, for the first time, entirely worthy of the applause.",
    "He had done this himself, with his own hands, and the satisfaction of it was immense.",
    "She watched her daughter accept the award and felt something swell in her chest that had no other name.",
    "He had told them it was possible. He had been right. He allowed himself a moment to savour that.",
    "She walked out of the presentation to a standing ovation and thought: I earned this.",
    "He was not a man who boasted. But privately, in his quietest moments, he was proud.",
    "She had come so far from where she had started. The distance was proof of something.",
    "He looked at what his team had built and felt a fierce, quiet joy.",
    "She had never done anything she was prouder of.",
    "He read his name on the list and straightened his back without quite knowing he was doing it.",
    "She had struggled for this, and it was hers, and no one could take the struggle away from her.",
    "He showed his father the letter and watched the old man's face change.",
    "She had doubted herself every step of the way. She was glad she had kept going.",
    "He could not stop smiling, and he was past caring who saw.",
    "She had done what people said could not be done. She intended to remember that.",
    "He had finally, after years of effort, proven himself — at least to himself, which was what mattered.",
    "She looked at her students and felt proud of every single one of them.",
    "He stood taller as he walked out of the building.",
    "The work was good. She knew it was good. For once she allowed herself to say so.",
    "He had given his best, and his best had been enough.",

    # ── DISAPPOINTMENT (target: 35 examples) ─────────────────────────────────
    # Label all of these as: 9 (disappointment)
    "She had hoped for so much more from him.",
    "He opened the results and felt the air leave his body.",
    "She had tried so hard, and it had not been enough. That was the part she could not make peace with.",
    "He had expected better. That was perhaps the most painful part.",
    "She put down the phone and sat very still, absorbing the news she had not wanted to receive.",
    "He had allowed himself to want it, which had been the mistake.",
    "She smiled and said she understood, and then went home and cried.",
    "The event was a letdown after all the anticipation.",
    "He gave everything he had to the audition. They called someone else.",
    "She had believed in him, completely, and he had let her down.",
    "He had imagined this moment so differently.",
    "She stared at the page and felt the slow deflation of hope.",
    "They had promised things they had not kept. She was too tired to be surprised.",
    "He said the words, but they were the wrong words, and she knew it was over.",
    "She had worked for months on something that ultimately no one cared about.",
    "He looked around the nearly empty room and tried not to show what he was feeling.",
    "She waited for the call that did not come.",
    "He had not expected perfection. He had expected more than this.",
    "She thought it would feel different, arriving at the end of something she had worked so long toward.",
    "He saw what they had done with his idea and barely recognised it.",

    # ── ANNOYANCE (target: 35 examples) ─────────────────────────────────────
    # Label all of these as: 3 (annoyance)
    "She wished, not for the first time, that he would simply listen.",
    "He had told them twice already. He was not going to tell them again.",
    "The noise had been going on for hours and she could feel it behind her eyes.",
    "He sighed heavily and pushed the papers aside.",
    "She had answered this question already. She answered it again, with diminishing patience.",
    "The meeting could have been an email. It had taken ninety minutes.",
    "He did not raise his voice. He did something worse — he became very quiet and very precise.",
    "She counted to ten, which helped, though not much.",
    "The constant interruptions made it impossible to think.",
    "He said nothing. But the set of his jaw said everything.",
    "She was not angry. She was, she told herself, simply tired of having to ask.",
    "He had been patient for a long time. His patience had reached its end.",
    "Why was this so difficult? She genuinely wanted to know.",
    "He clicked the pen. Once. Twice. Three times. She looked up.",
    "She closed the door a little harder than was strictly necessary.",
    "He was not in the mood. He had not been in the mood all morning.",
    "She chose her words carefully, which took effort, because her instinct was to say something sharp.",
    "The apology was too late and too little, and she let him know it.",
    "He had asked nicely. He had asked firmly. He was running out of options.",
    "She replied with the minimum number of words that could be considered a reply.",
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
