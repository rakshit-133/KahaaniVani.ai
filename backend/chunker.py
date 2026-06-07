import spacy

# Loaded once at startup, reused for every request
_nlp = None


def load_chunker():
    """
    Load the spaCy English model into memory.
    Call this once at server startup, not per request.
    """
    global _nlp
    print("Loading spaCy model (en_core_web_sm)...")
    _nlp = spacy.load("en_core_web_sm")
    print("spaCy model loaded.")


def split_into_chunks(text: str, max_tokens: int = 300) -> list[str]:
    """
    Split input text into sentence-level chunks using spaCy's neural
    sentence boundary detector.

    Handles edge cases regex cannot:
      - Abbreviations: "Dr. Smith" stays together
      - Decimals: "3.14 degrees" stays together  
      - Ellipsis: "She said... nothing" stays together

    Merges short sentences until approaching max_tokens, to avoid
    feeding single-word fragments to the emotion model.

    Args:
        text: raw input paragraph from the user
        max_tokens: soft upper limit per chunk (model hard limit is 512)

    Returns:
        list of clean sentence-chunk strings
    """
    if _nlp is None:
        raise RuntimeError("spaCy model not loaded. Call load_chunker() first.")

    # Run the full spaCy pipeline — sentence boundaries are detected here
    doc = _nlp(text.strip())

    # Extract sentence strings from the Doc object
    sentences = [sent.text.strip() for sent in doc.sents]

    chunks = []   # final output
    current = ""  # accumulator

    for sentence in sentences:
        if not sentence:
            continue

        # Test what the chunk would look like with this sentence added
        candidate = (current + " " + sentence).strip()

        # Rough token estimate: tokenizers split words into subword pieces,
        # so multiply word count by 1.3 as a conservative buffer
        estimated_tokens = len(candidate.split()) * 1.3

        if estimated_tokens > max_tokens and current:
            # Over budget — save current chunk, start fresh
            chunks.append(current.strip())
            current = sentence
        else:
            # Still under budget — keep accumulating
            current = candidate

    # Save the final accumulated group (loop never saves the last one)
    if current.strip():
        chunks.append(current.strip())

    # Filter out fragments shorter than 10 characters
    return [c for c in chunks if len(c) > 10]