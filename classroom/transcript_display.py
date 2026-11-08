"""Presentation-only grouping; never repair or rewrite recognized words."""
import re

LATIN_RUN = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:[ \t]+[A-Za-z][A-Za-z0-9_]*)*")


def reading_paragraphs(text, segments):
    """Use trusted segment boundaries only when they reconstruct stored full text.

    Break at >=0.8s gaps, ~25s speech blocks or ~360 characters. Individual
    segments stay intact; these are reading aids, not semantic paragraphs.
    Older/unmatched results retain their exact text in one block.
    """
    parts = [item['text'].strip() for item in segments]
    if not parts or ' '.join(parts).strip() != text:
        blocks = [text]
    else:
        blocks = []
        current = []
        block_start = previous_end = None
        for item, part in zip(segments, parts):
            start, end = item['start'], item['end']
            if current and (start - previous_end >= 0.8 or
                            end - block_start > 25 or
                            sum(map(len, current)) + len(current) + len(part) > 360):
                blocks.append(' '.join(current))
                current = []
            if not current:
                block_start = start
            current.append(part)
            previous_end = end
        if current:
            blocks.append(' '.join(current))
    paragraphs = []
    for block in blocks:
        runs = []
        position = 0
        for match in LATIN_RUN.finditer(block):
            if match.start() > position:
                runs.append({'text': block[position:match.start()], 'latin': False})
            runs.append({'text': match.group(), 'latin': True})
            position = match.end()
        if position < len(block):
            runs.append({'text': block[position:], 'latin': False})
        paragraphs.append(runs)
    return paragraphs
