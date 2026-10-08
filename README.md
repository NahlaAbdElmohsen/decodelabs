# Rule-Based Chatbot

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

A small command-line customer-support chatbot written in pure Python (standard library only). It uses prioritized regex intents, a light conversation state, and fuzzy matching so it still understands typos like *"prodcts"*.

## Demo

```text
Bot: Hello! What's your name?
You: my name is ahmed
Bot: Nice to meet you, Ahmed! How can I help you today?
You: hi!
Bot: Greetings, Ahmed!
You: Tell me about prodcts
Bot: We have a great selection of products! Which one are you interested in?
You: the blue one
Bot: Good choice! I've noted your interest in 'the blue one'. A team member will follow up. Anything else I can help with?
You: no
Bot: Alright, Ahmed. Have a great day!
```

## Features

- **Intent table:** each intent is one `(name, regex pattern, replies)` entry, listed in priority order. Adding a new intent takes one line.
- **Built-in intents:** greeting, farewell, thanks, pricing, opening hours, order status, products, and support, plus a helpful fallback reply.
- **Conversation state:** after "products" or "support", the next message is treated as the answer. Yes/no is interpreted only when the bot has just asked "Anything else?", so "I have no problem with your products" is not read as a "no".
- **Typo tolerance:** input is lowercased, punctuation is stripped, and near-miss words are corrected with `difflib`.
- **Personalization:** the bot extracts the user's name ("Ahmed", "my name is Ahmed", "I'm Ahmed") and uses it in replies.
- **Robust I/O:** empty input is handled, and Ctrl+C / Ctrl+D exit cleanly.
- **Testable design:** `get_response(text)` returns `(intent, reply)` and does no `input()` or `print()`.

## Getting started

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python chatbot.py
```

No packages need to be installed. Say `bye`, `goodbye`, `quit`, or `exit` to end the chat.

## How it works

1. `normalize()` lowercases the message, removes punctuation, and fixes words that are close to known keywords (similarity cutoff 0.8).
2. If the bot is waiting for an answer (`self.pending`), `_handle_pending()` interprets the message first. A goodbye always bypasses this.
3. Otherwise the intents are checked in order, and the first matching pattern wins. The reply is chosen at random from that intent's replies.
4. The main loop in `run()` repeats until the `farewell` intent is returned.

### Adding an intent

```python
("returns", r"\b(return|refund|exchange)\b",
 ["You can return items within 30 days. Do you have your order number?"]),
```

Add it to `self.intents` in priority order. Words of four or more letters in the pattern are automatically used for typo correction.

## Project structure

```text
.
├── chatbot.py    # the chatbot (single file)
└── README.md
```

## Limitations and ideas for improvement

- Matching is keyword-based, so the bot has no real language understanding.
- Fuzzy matching can occasionally "correct" a legitimate word into a keyword.
- Ideas: unit tests with `pytest` for `get_response`, keyword scoring instead of first-match, a larger intent set loaded from a JSON file, multi-turn slots (for example, collecting an order number), and a web or Telegram front end.

## License

Add a `LICENSE` file (for example MIT) before publishing.
